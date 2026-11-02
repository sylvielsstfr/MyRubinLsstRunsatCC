"""Read and use the_monster reference catalog through the Butler.

Adapted from LSSTDESC/spesn (spesn/io.py), with these differences:

- no TAP / RSP dependency: everything goes through the Butler
  (works with the ``main`` and ``dp2`` community butlers at CC-IN2P3);
- HTM sharding is done with ``lsst.sphgeom`` (no ``esutil`` needed);
- survey/band/flux column discovery is generic (no hard-coded ComCam names);
- unit handling is explicit and checked, not assumed.

The reference copy of the original code is kept untouched in ``src/spesn/io.py``.

NOTE: this code was written without access to the Butler, so it has to be
validated on the first run (see notebooks/05_AnaStep1/00_theMonster.ipynb).
"""

from __future__ import annotations

import re
from typing import Any, Iterable

import numpy as np
import pandas as pd

DEFAULT_MONSTER_DATASET = "the_monster_20250219"
HTM_LEVEL = 7

# <prefix>_<band>_flux or <prefix>_<band>_fluxErr, e.g. monster_ComCam_g_flux
_FLUX_RE = re.compile(r"^(?P<prefix>.+)_(?P<band>[ugrizy])_(?P<kind>flux|fluxErr)$")


# ----------------------------------------------------------------------------
# Butler access
# ----------------------------------------------------------------------------
def get_butler(repo: str = "main", collections: str | list[str] | None = None) -> Any:
    """Return a Butler for a community repository (e.g. 'main' or 'dp2')."""
    from lsst.daf.butler import Butler

    if collections is None:
        return Butler(repo)
    return Butler(repo, collections=collections)


def find_monster_dataset_types(butler: Any, pattern: str = "*monster*") -> list[str]:
    """List the dataset types whose name matches a glob pattern."""
    return sorted(dt.name for dt in butler.registry.queryDatasetTypes(pattern))


def find_collections_with_dataset(
    butler: Any,
    dataset_type: str,
    collection_glob: str = "*",
    max_collections: int = 200,
) -> list[str]:
    """Return the collections (among those matching a glob) holding a dataset type.

    This can be slow on large repositories: narrow ``collection_glob`` if needed.
    """
    found: list[str] = []
    for name in butler.registry.queryCollections(collection_glob):
        if len(found) >= max_collections:
            break
        try:
            has_dataset = False
            for _ in butler.registry.queryDatasets(dataset_type, collections=name, findFirst=False):
                has_dataset = True
                break
        except Exception:
            continue
        if has_dataset:
            found.append(name)
    return found


# ----------------------------------------------------------------------------
# HTM sharding
# ----------------------------------------------------------------------------
def htm_ids_for_cone(ra_deg: float, dec_deg: float, radius_deg: float, level: int = HTM_LEVEL) -> list[int]:
    """HTM pixel ids (at ``level``) overlapping a cone on the sky."""
    import lsst.sphgeom as sphgeom

    center = sphgeom.UnitVector3d(sphgeom.LonLat.fromDegrees(ra_deg, dec_deg))
    circle = sphgeom.Circle(center, sphgeom.Angle.fromDegrees(radius_deg))
    pixelization = sphgeom.HtmPixelization(level)
    ranges = pixelization.envelope(circle)
    ids: list[int] = []
    for begin, end in ranges.ranges():
        ids.extend(range(begin, end))
    return ids


def htm_ids_for_points(ra_deg: Iterable[float], dec_deg: Iterable[float], level: int = HTM_LEVEL) -> list[int]:
    """Unique HTM pixel ids (at ``level``) containing a set of points."""
    import lsst.sphgeom as sphgeom

    pixelization = sphgeom.HtmPixelization(level)
    ids = set()
    for ra, dec in zip(np.asarray(ra_deg, dtype=float), np.asarray(dec_deg, dtype=float)):
        point = sphgeom.UnitVector3d(sphgeom.LonLat.fromDegrees(float(ra), float(dec)))
        ids.add(int(pixelization.index(point)))
    return sorted(ids)


# ----------------------------------------------------------------------------
# Loading the catalog
# ----------------------------------------------------------------------------
def _as_astropy(obj: Any) -> Any:
    """Convert whatever the Butler returned into an astropy Table."""
    if hasattr(obj, "asAstropy"):
        return obj.asAstropy()
    if hasattr(obj, "to_pandas") and not hasattr(obj, "colnames"):
        from astropy.table import Table

        return Table.from_pandas(obj.to_pandas())
    return obj


def to_degrees(values: Any) -> np.ndarray:
    """Convert a coordinate column to degrees.

    - if the column carries an astropy unit, use it;
    - otherwise values within [-2*pi, 2*pi] are assumed to be radians,
      anything larger is assumed to be degrees (safe for fields such as COSMOS,
      RA ~ 150 deg, but NOT for a patch of sky very close to RA = 0 and Dec = 0:
      check the unit explicitly in the notebook).
    """
    if hasattr(values, "unit") and values.unit is not None:
        import astropy.units as u

        try:
            return np.asarray(values.to(u.deg).value, dtype=float)
        except Exception:
            pass
    arr = np.asarray(values, dtype=float)
    finite = np.isfinite(arr)
    if finite.any() and np.nanmax(np.abs(arr[finite])) <= 2.0 * np.pi + 0.1:
        return np.rad2deg(arr)
    return arr


def load_monster_shards(
    butler: Any,
    htm_ids: Iterable[int],
    dataset: str = DEFAULT_MONSTER_DATASET,
    collections: str | list[str] | None = None,
    verbose: bool = True,
) -> Any:
    """Load and stack the requested HTM7 shards (missing shards are skipped)."""
    from astropy.table import vstack

    tables = []
    for htm_id in htm_ids:
        kwargs: dict[str, Any] = {"htm7": int(htm_id)}
        try:
            obj = butler.get(dataset, collections=collections, **kwargs) if collections else butler.get(dataset, **kwargs)
        except Exception as exc:  # shard absent or not readable
            if verbose:
                print(f"htm7={htm_id}: skipped ({type(exc).__name__})")
            continue
        tab = _as_astropy(obj)
        if verbose:
            print(f"htm7={htm_id}: {len(tab)} rows")
        tables.append(tab)
    if not tables:
        return None
    return vstack(tables, metadata_conflicts="silent")


def load_monster_cone(
    butler: Any,
    ra_deg: float,
    dec_deg: float,
    radius_deg: float,
    dataset: str = DEFAULT_MONSTER_DATASET,
    collections: str | list[str] | None = None,
    ra_col: str = "coord_ra",
    dec_col: str = "coord_dec",
    verbose: bool = True,
) -> pd.DataFrame:
    """Return the Monster rows within a cone, as a DataFrame with ra_deg/dec_deg columns."""
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    ids = htm_ids_for_cone(ra_deg, dec_deg, radius_deg)
    if verbose:
        print(f"{len(ids)} HTM{HTM_LEVEL} shards overlap the cone")
    tab = load_monster_shards(butler, ids, dataset=dataset, collections=collections, verbose=verbose)
    if tab is None:
        return pd.DataFrame()

    ra = to_degrees(tab[ra_col])
    dec = to_degrees(tab[dec_col])
    center = SkyCoord(ra_deg * u.deg, dec_deg * u.deg)
    sep = center.separation(SkyCoord(ra * u.deg, dec * u.deg)).deg
    keep = sep <= radius_deg

    df = _table_to_pandas(tab[keep])
    df["ra_deg"] = ra[keep]
    df["dec_deg"] = dec[keep]
    return df


def _table_to_pandas(tab: Any) -> pd.DataFrame:
    """astropy Table -> DataFrame, dropping multi-dimensional columns if needed."""
    try:
        return tab.to_pandas()
    except Exception:
        scalar = [n for n in tab.colnames if len(tab[n].shape) <= 1]
        return tab[scalar].to_pandas()


# ----------------------------------------------------------------------------
# Column discovery and photometric helpers
# ----------------------------------------------------------------------------
def discover_flux_columns(colnames: Iterable[str]) -> pd.DataFrame:
    """Parse '<prefix>_<band>_flux[Err]' column names into a tidy table."""
    rows = []
    for name in colnames:
        match = _FLUX_RE.match(name)
        if match:
            rows.append({"column": name, **match.groupdict()})
    return pd.DataFrame(rows, columns=["column", "prefix", "band", "kind"])


def flux_njy_to_abmag(flux_njy: Any) -> np.ndarray:
    """AB magnitude from a flux in nJy: m = 31.4 - 2.5 log10(f)."""
    f = np.asarray(flux_njy, dtype=float)
    out = np.full_like(f, np.nan, dtype=float)
    good = np.isfinite(f) & (f > 0)
    out[good] = 31.4 - 2.5 * np.log10(f[good])
    return out


def abmag_to_flux_njy(mag: Any) -> np.ndarray:
    """Flux in nJy from an AB magnitude."""
    return 10.0 ** ((31.4 - np.asarray(mag, dtype=float)) / 2.5)


# ----------------------------------------------------------------------------
# Cross-match
# ----------------------------------------------------------------------------
def crossmatch(
    ra1_deg: Any,
    dec1_deg: Any,
    ra2_deg: Any,
    dec2_deg: Any,
    max_sep_arcsec: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Nearest neighbour of each point of catalog 1 in catalog 2.

    Returns (index_in_2, separation_arcsec, matched_mask).
    """
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    c1 = SkyCoord(np.asarray(ra1_deg, dtype=float) * u.deg, np.asarray(dec1_deg, dtype=float) * u.deg)
    c2 = SkyCoord(np.asarray(ra2_deg, dtype=float) * u.deg, np.asarray(dec2_deg, dtype=float) * u.deg)
    idx, d2d, _ = c1.match_to_catalog_sky(c2)
    sep = d2d.arcsec
    return np.asarray(idx), np.asarray(sep), sep < float(max_sep_arcsec)
