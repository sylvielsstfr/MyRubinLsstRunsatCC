"""Helpers to browse and display the lsst.analysis.tools plots stored in a Butler collection.

Used by the notebooks nb2026-11-06_ShowPlots_DRPstage1-single-visit.ipynb
and nb2026-11-06_ShowPlots_DRPstage2-recalibrate.ipynb.

Notes
-----
- Plot datasets (storage class 'Plot') are written as image files (PNG) by the pipeline.
  They cannot be read back as matplotlib figures with butler.get(), so the files are
  retrieved with butler.retrieveArtifacts() and displayed from disk.
- Files already present in raw_dir are not downloaded again.
"""

import collections
import math
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import Image, Markdown, display

BAND_ORDER = 'ugrizy'

# Dimensions used to split a set of plots into panels (first one with several values wins)
FACET_PRIORITY = ('band', 'physical_filter', 'visit', 'detector', 'tract', 'patch')


def dval(ref, key):
    """Value of a dimension in the dataId of a dataset reference (None if the dimension is absent)."""
    try:
        return ref.dataId[key]
    except KeyError:
        return None


def _facet_sort_key(value):
    """Sort key : bands in ugrizy order, then other values, None last."""
    if value is None:
        return (2, 0)
    if isinstance(value, str) and value in BAND_ORDER and len(value) == 1:
        return (0, BAND_ORDER.index(value))
    return (1, value)


def pick_facet(refs):
    """First dimension of FACET_PRIORITY taking several values in refs (None if there is none)."""
    for key in FACET_PRIORITY:
        if len({dval(r, key) for r in refs}) > 1:
            return key
    return None


def kind_of(short_name):
    """Kind of plot from the dataset type name, e.g. 'HistPlot', 'FocalPlanePlot', 'WholeSkyPlot'."""
    m = re.search(r'([A-Za-z0-9]*Plot)$', short_name)
    return m.group(1) if m else ''


def show_diagram(path, title=None, width=1000):
    """Display a PNG file (here a pipeline quantum diagram)."""
    path = Path(path)
    if not path.exists():
        print('File not found :', path.resolve())
        return
    if title:
        display(Markdown(f'### {title}'))
    display(Image(filename=str(path), width=width))


class PlotBrowser:
    """Browse and display all the Plot datasets of one Butler collection.

    Parameters
    ----------
    butler : lsst.daf.butler.Butler
    collection : str or list of str
        Collection (e.g. the stage1 output) or list of collections (e.g. the RUN collections written by
        stage 2) containing the plots.
    raw_dir : str or Path
        Directory where the plot files are retrieved.
    montage_dir : str or Path, optional
        Directory where the montages are saved (default: raw_dir/montages).
    dataset_type_glob : str
        Glob selecting the plot dataset types.
    find_first : bool
        True : one dataset per dataId (the first one found in the collection order, i.e. the latest run).
    strip_prefix : bool
        True : the common prefix of the dataset type names is removed from the 'short' names.
        False : the 'short' names are the full dataset type names.
    """

    def __init__(self, butler, collection, raw_dir, montage_dir=None, dataset_type_glob='*Plot',
                 find_first=False, strip_prefix=True):
        self.butler = butler
        self.collection = collection
        self.find_first = find_first
        self.raw_dir = Path(raw_dir)
        self.montage_dir = Path(montage_dir) if montage_dir else self.raw_dir / 'montages'
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.montage_dir.mkdir(parents=True, exist_ok=True)

        refs = list(
            butler.registry.queryDatasets(
                datasetType=dataset_type_glob,
                collections=collection,
                findFirst=find_first,
            )
        )

        # Common prefix of the dataset type names (cut after an underscore), removed in 'short'
        names = sorted({r.datasetType.name for r in refs})
        prefix = os.path.commonprefix(names)
        self.prefix = prefix[:prefix.rfind('_') + 1] if strip_prefix else ''

        columns = ['short', 'datasetType', *FACET_PRIORITY, 'ref']
        rows = []
        for r in refs:
            row = {'short': r.datasetType.name[len(self.prefix):], 'datasetType': r.datasetType.name}
            for key in FACET_PRIORITY:
                row[key] = dval(r, key)
            row['ref'] = r
            rows.append(row)
        self.df = pd.DataFrame(rows, columns=columns)

    # ------------------------------------------------------------------ tables
    def summary(self):
        """One row per plot dataset type : number of datasets, dimensions, storage class, kind of plot."""
        rows = []
        for short, grp in self.df.groupby('short'):
            refs = list(grp['ref'])
            dt = refs[0].datasetType
            rows.append({
                'short': short,
                'n': len(refs),
                'dimensions': ', '.join(dt.dimensions.names),
                'storageClass': dt.storageClass_name,
                'kind': kind_of(short),
            })
        if not rows:
            return pd.DataFrame(columns=['n', 'dimensions', 'storageClass', 'kind'])
        return pd.DataFrame(rows).set_index('short')

    def completeness(self, facet='band'):
        """Number of plots per dataset type and per value of a dimension (to spot missing plots)."""
        sub = self.df[self.df[facet].notna()]
        if sub.empty:
            return pd.DataFrame()
        table = sub.pivot_table(index='short', columns=facet, values='ref', aggfunc='count', fill_value=0)
        return table[sorted(table.columns, key=_facet_sort_key)]

    def select(self, pattern=None, **facets):
        """Rows of the table matching a regex on the short name and/or dimension values.

        Example : select('HistPlot$', band='i') or select(band=['g', 'r', 'i'])
        """
        mask = pd.Series(True, index=self.df.index)
        if pattern:
            mask &= self.df['short'].apply(lambda s: re.search(pattern, s) is not None)
        for key, value in facets.items():
            if isinstance(value, (list, tuple, set)):
                mask &= self.df[key].isin(list(value))
            else:
                mask &= self.df[key] == value
        return self.df[mask]

    # ------------------------------------------------------------- retrieval
    def ensure_local(self, refs):
        """Retrieve the files of refs not yet in raw_dir. Returns {ref.id: local Path}."""
        paths, missing = {}, []
        for ref in refs:
            path = self.raw_dir / self.butler.getURI(ref).basename()
            paths[ref.id] = path
            if not path.exists():
                missing.append(ref)
        if missing:
            print(f'Retrieving {len(missing)} plot file(s) into {self.raw_dir} ...')
            self.butler.retrieveArtifacts(
                missing, destination=self.raw_dir, preserve_path=False, overwrite=True
            )
        return paths

    # --------------------------------------------------------------- display
    def show_images(self, refs, width=900):
        """Display each plot at full resolution (one after the other)."""
        refs = list(refs)
        paths = self.ensure_local(refs)
        for ref in refs:
            display(Markdown(f'**{ref.datasetType.name}**  \n`{ref.dataId}`'))
            display(Image(filename=str(paths[ref.id]), width=width))

    def show_montage(self, refs, title=None, ncols=3, max_panels=12, save=True, dpi=100):
        """Display the plots of one dataset type side by side (e.g. one panel per band).

        The panels are split with the first dimension taking several values (band, visit, ...).
        If other dimensions (e.g. tract) take several values, one montage is made per value.
        """
        refs = list(refs)
        if not refs:
            print('Nothing to show')
            return
        paths = self.ensure_local(refs)

        facet = pick_facet(refs)
        others = [k for k in FACET_PRIORITY if k != facet]
        groups = collections.defaultdict(list)
        for r in refs:
            groups[tuple(dval(r, k) for k in others)].append(r)

        for gkey in sorted(groups, key=lambda g: tuple(str(x) for x in g)):
            grp = sorted(groups[gkey], key=lambda r: _facet_sort_key(dval(r, facet)) if facet else (0, 0))
            glabel = ', '.join(f'{k}={v}' for k, v in zip(others, gkey) if v is not None)

            for page, start in enumerate(range(0, len(grp), max_panels)):
                chunk = grp[start:start + max_panels]
                ncol = min(ncols, len(chunk))
                nrow = math.ceil(len(chunk) / ncol)
                fig, axes = plt.subplots(nrow, ncol, figsize=(6.0 * ncol, 4.5 * nrow), squeeze=False)
                for ax in axes.ravel():
                    ax.axis('off')

                for ax, ref in zip(axes.ravel(), chunk):
                    label = f'{facet}={dval(ref, facet)}' if facet else str(ref.dataId)
                    try:
                        ax.imshow(plt.imread(str(paths[ref.id])))
                    except Exception as exc:  # unreadable file : keep the panel, show the reason
                        ax.text(0.5, 0.5, f'cannot read {paths[ref.id].name}\n{exc}',
                                ha='center', va='center', fontsize=8)
                    ax.set_title(label, fontsize=13)

                head = ' | '.join(x for x in (title or chunk[0].datasetType.name, glabel) if x)
                fig.suptitle(head, fontsize=12)
                fig.tight_layout(rect=(0, 0, 1, 0.97))
                if save:
                    stem = re.sub(r'[^A-Za-z0-9_.=-]+', '_', head) + (f'_p{page}' if page else '')
                    fig.savefig(self.montage_dir / f'{stem}.png', dpi=dpi, bbox_inches='tight')
                plt.show()
                plt.close(fig)

    def show(self, pattern=None, mode='montage', ncols=3, max_types=None, max_refs=None, **facets):
        """Display the plots matching a regex on the short name and/or dimension values.

        mode : 'montage' (one figure per dataset type, one panel per band/visit/...)
               or 'single' (each plot alone, full resolution).
        max_types, max_refs : safety limits on the number of dataset types / plots displayed.
        """
        sub = self.select(pattern, **facets)
        if sub.empty:
            print('No plot matches', pattern, facets)
            return

        shorts = sorted(sub['short'].unique())
        if max_types is not None and len(shorts) > max_types:
            print(f'{len(shorts)} dataset types match, showing the first {max_types} (max_types)')
            shorts = shorts[:max_types]

        for short in shorts:
            refs = list(sub.loc[sub['short'] == short, 'ref'])
            if max_refs is not None and len(refs) > max_refs:
                print(f'{short} : {len(refs)} plots, showing the first {max_refs} (max_refs)')
                refs = refs[:max_refs]
            if mode == 'montage':
                self.show_montage(refs, title=short, ncols=ncols)
            else:
                self.show_images(refs)

    # ------------------------------------------------- other datasets (metrics)
    def dataset_types(self):
        """Names of all the dataset types of the collection (from the collection summary)."""
        collections = [self.collection] if isinstance(self.collection, str) else list(self.collection)
        try:
            names = set()
            for collection in collections:
                info = self.butler.collections.get_info(collection, include_summary=True)
                names.update(info.dataset_types)
            return sorted(names)
        except Exception as exc:
            print('Collection summary not available :', exc)
            return []

    def sibling_types(self, contains='metric'):
        """Non-plot dataset types of the collection whose name contains a string (e.g. the metrics)."""
        return [n for n in self.dataset_types()
                if contains.lower() in n.lower() and not n.endswith('Plot')]

    def load_first(self, dataset_type):
        """Read the first dataset of a given type in the collection (None if there is none)."""
        refs = list(
            self.butler.registry.queryDatasets(
                datasetType=dataset_type, collections=self.collection, findFirst=self.find_first
            )
        )
        print(f'{len(refs)} dataset(s) of type {dataset_type}')
        if not refs:
            return None
        print('dataId :', refs[0].dataId)
        obj = self.butler.get(refs[0])
        print('type   :', type(obj))
        return obj
