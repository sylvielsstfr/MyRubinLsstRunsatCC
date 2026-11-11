#!/usr/bin/env python
'''Build an fgcm atmosphere table (FITS) from the getObsAtmo libRadtran emulator.

The table has the layout written by fgcm.FgcmAtmosphereTable.saveTable():

  PARS    one-row binary table : grids (PMB, LNPWV, O3, LNTAU, ALPHA, SECZENITH), standard values,
          ATMLAMBDA (Angstrom), ATMSTDTRANS (standard atmosphere transmission), ...
  PWVATM  H2O transmission, shape (n_pwv + 1, n_zenith + 1, n_lambda)
  O3ATM   O3 transmission,  shape (n_o3  + 1, n_zenith + 1, n_lambda)
  O2ATM   O2 transmission,  shape (n_zenith + 1, n_lambda)
  RAYATM  Rayleigh transmission, shape (n_zenith + 1, n_lambda)

Each grid axis has one extra point (last value + delta) because fgcm interpolates between nodes.
Aerosols are NOT in the table : fgcm applies exp(-tau * secZ * (lambda / lambdaNorm)^-alpha) itself,
with lambdaNorm = 7750 Angstrom. The same formula is used here for ATMSTDTRANS (getObsAtmo uses another
normalisation, 500 nm, which is not used here).

Pressure : the components are the ones of getObsAtmo at the reference pressure of the site, which is stored
as PMBELEVATION, so that fgcm's pressure factor is 1 at that pressure.

Usage
-----
    python make_fgcm_atm_table_from_obsatmo.py -o fgcm_atm_lsst_obsatmo.fits --check \\
        --reference /path/to/fgcm/fgcm/data/tables/fgcm_atm_lsst2.fits
'''
import argparse
import datetime
import os
import sys

import numpy as np
from astropy.io import fits

from getObsAtmo.getObsAtmo import ObsAtmo, Dict_Of_sitesAltitudes

LAMBDA_NORM = 7750.0       # Angstrom, as in fgcm
MAX_PWV = 20.0             # mm, as in fgcm.FgcmAtmosphereTable.generateTable


def aerosol_transmission(lam_angstrom, sec_z, tau, alpha, lambda_norm=LAMBDA_NORM):
    '''Aerosol transmission with the fgcm parametrization (tau defined at lambda_norm).'''
    return np.exp(-tau * sec_z * (lam_angstrom / lambda_norm) ** (-alpha))


def build_table(args):
    '''Evaluate the emulator on the fgcm grids and return the content of the table.'''
    emul = ObsAtmo(args.site, pressure=0)           # grids at the reference pressure of the site
    pmb_elevation = float(emul.refpressure)
    elevation = 1000.0 * Dict_Of_sitesAltitudes[emul.OBS_tag]

    # ---- wavelength grid (Angstrom) : fgcm uses lambdaRange in Angstrom and lambdaStep in nm
    lam_range = np.array(args.lambda_range, dtype=float)
    step_angstrom = 10.0 * args.lambda_step
    n_lam = int(round((lam_range[1] - lam_range[0]) / step_angstrom)) + 1
    atm_lambda = lam_range[0] + step_angstrom * np.arange(n_lam)
    lam_nm = atm_lambda / 10.0
    wl_grid = np.asarray(emul.GetWL())
    lam_nm = np.clip(lam_nm, wl_grid.min(), wl_grid.max())     # protect against rounding at the edges

    # ---- parameter grids, same construction as FgcmAtmosphereTable.generateTable
    pmb = np.linspace(args.pmb_range[0], args.pmb_range[1], num=args.pmb_steps)
    ln_pwv = np.linspace(np.log(args.pwv_range[0]), np.log(args.pwv_range[1]), num=args.pwv_steps)
    o3 = np.linspace(args.o3_range[0], args.o3_range[1], num=args.o3_steps)
    ln_tau = np.linspace(np.log(args.tau_range[0]), np.log(args.tau_range[1]), num=args.tau_steps)
    alpha = np.linspace(args.alpha_range[0], args.alpha_range[1], num=args.alpha_steps)
    sec_zenith = np.linspace(1.0, args.airmass_max, num=args.zenith_steps)

    ln_pwv_delta = ln_pwv[1] - ln_pwv[0]
    o3_delta = o3[1] - o3[0]
    sec_delta = sec_zenith[1] - sec_zenith[0]

    ln_pwv_plus = np.minimum(np.append(ln_pwv, ln_pwv[-1] + ln_pwv_delta), np.log(MAX_PWV))
    pwv_plus = np.exp(ln_pwv_plus)
    o3_plus = np.append(o3, o3[-1] + o3_delta)
    sec_plus = np.append(sec_zenith, sec_zenith[-1] + sec_delta)

    am_max = float(np.max(emul.GetObsAtmoAirmass())) if hasattr(emul, 'GetObsAtmoAirmass') else 2.6
    if sec_plus[-1] > am_max + 1e-6:
        raise ValueError(f'last airmass node {sec_plus[-1]:.4f} is above the emulator limit {am_max}; '
                         'reduce --airmass-max or --zenith-steps')
    if pwv_plus[-1] > 20.25 or o3_plus[-1] > 625.0:
        raise ValueError('pwv or o3 grid goes beyond the emulator grid (20.25 mm, 625 DU)')
    sec_plus = np.minimum(sec_plus, am_max)

    # ---- components
    pwv_atm = np.zeros((pwv_plus.size, sec_plus.size, n_lam))
    for i, pwv in enumerate(pwv_plus):
        for j, am in enumerate(sec_plus):
            pwv_atm[i, j, :] = emul.GetPWVabsTransparencyArray(lam_nm, am, pwv)

    o3_atm = np.zeros((o3_plus.size, sec_plus.size, n_lam))
    for i, oz in enumerate(o3_plus):
        for j, am in enumerate(sec_plus):
            o3_atm[i, j, :] = emul.GetOZabsTransparencyArray(lam_nm, am, oz)

    o2_atm = np.zeros((sec_plus.size, n_lam))
    ray_atm = np.zeros((sec_plus.size, n_lam))
    for j, am in enumerate(sec_plus):
        o2_atm[j, :] = emul.GetO2absTransparencyArray(lam_nm, am)
        ray_atm[j, :] = emul.GetRayleighTransparencyArray(lam_nm, am)

    # ---- standard atmosphere (at the standard pressure), aerosols with the fgcm formula
    pmb_std = pmb_elevation if args.pmb_std is None else args.pmb_std
    emul_std = ObsAtmo(args.site, pressure=pmb_std)
    std_gridded = emul_std.GetAllTransparencies(lam_nm, args.airmass_std, args.pwv_std, args.o3_std,
                                                flagAerosols=False)
    atm_std_trans = std_gridded * aerosol_transmission(atm_lambda, args.airmass_std,
                                                       args.tau_std, args.alpha_std)

    pars = dict(
        ELEVATION=elevation, PMBELEVATION=pmb_elevation, PMBSTD=pmb_std, PWVSTD=args.pwv_std,
        O3STD=args.o3_std, TAUSTD=args.tau_std, ALPHASTD=args.alpha_std, AIRMASSSTD=args.airmass_std,
        LAMBDARANGE=lam_range, LAMBDASTEP=args.lambda_step, LAMBDANORM=LAMBDA_NORM,
        ATMLAMBDA=atm_lambda, ATMSTDTRANS=atm_std_trans,
        PMB=pmb, PMBDELTA=pmb[1] - pmb[0],
        LNPWV=ln_pwv, LNPWVDELTA=ln_pwv_delta,
        O3=o3, O3DELTA=o3_delta,
        LNTAU=ln_tau, LNTAUDELTA=ln_tau[1] - ln_tau[0],
        ALPHA=alpha, ALPHADELTA=alpha[1] - alpha[0],
        SECZENITH=sec_zenith, SECZENITHDELTA=sec_delta,
    )
    return pars, pwv_atm, o3_atm, o2_atm, ray_atm


PARS_ORDER = ['ELEVATION', 'PMBELEVATION', 'PMBSTD', 'PWVSTD', 'O3STD', 'TAUSTD', 'ALPHASTD', 'AIRMASSSTD',
              'LAMBDARANGE', 'LAMBDASTEP', 'LAMBDANORM', 'ATMLAMBDA', 'ATMSTDTRANS', 'PMB', 'PMBDELTA',
              'LNPWV', 'LNPWVDELTA', 'O3', 'O3DELTA', 'LNTAU', 'LNTAUDELTA', 'ALPHA', 'ALPHADELTA',
              'SECZENITH', 'SECZENITHDELTA']


def write_table(filename, pars, pwv_atm, o3_atm, o2_atm, ray_atm, args, clobber=False):
    '''Write the table with the same HDUs and column names as FgcmAtmosphereTable.saveTable.'''
    columns = []
    for name in PARS_ORDER:
        value = np.atleast_1d(np.asarray(pars[name], dtype='f4'))
        fmt = 'E' if value.size == 1 else f'{value.size}E'
        columns.append(fits.Column(name=name, format=fmt, array=value.reshape(1, -1)
                                   if value.size > 1 else value))
    pars_hdu = fits.BinTableHDU.from_columns(columns, name='PARS')

    primary = fits.PrimaryHDU()
    primary.header['COMMENT'] = 'fgcm atmosphere table built from the getObsAtmo libRadtran emulator'
    primary.header['OBSSITE'] = args.site
    primary.header['CREATED'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        from getObsAtmo import _version
        primary.header['OBSATMO'] = str(_version.version)
    except Exception:
        pass

    hdul = fits.HDUList([primary, pars_hdu,
                         fits.ImageHDU(pwv_atm, name='PWVATM'),
                         fits.ImageHDU(o3_atm, name='O3ATM'),
                         fits.ImageHDU(o2_atm, name='O2ATM'),
                         fits.ImageHDU(ray_atm, name='RAYATM')])
    hdul.writeto(filename, overwrite=clobber)
    print(f'written {filename}')


def check_with_fgcm(filename, args, reference=None, figure=None):
    '''Read the table back with fgcm, compare with the emulator and (optionally) with a reference table.'''
    try:
        from fgcm.fgcmAtmosphereTable import FgcmAtmosphereTable
    except Exception as exc:
        print(f'fgcm not importable ({type(exc).__name__}: {exc}) : no check with fgcm')
        return

    new = FgcmAtmosphereTable.initWithTableName(filename)
    new.loadTable()
    print('read back with fgcm : OK')

    emul = ObsAtmo(args.site, pressure=0)
    test_points = [
        dict(pwv=3.0, o3=263.0, tau=0.03, alpha=1.0, zenith=np.degrees(np.arccos(1 / 1.2))),
        dict(pwv=1.0, o3=240.0, tau=0.01, alpha=1.5, zenith=np.degrees(np.arccos(1 / 1.5))),
        dict(pwv=7.5, o3=300.0, tau=0.1, alpha=0.5, zenith=np.degrees(np.arccos(1 / 2.0))),
    ]
    lam = new.atmLambda
    print('\nfgcm interpolation of the new table vs direct emulator (pressure = reference) :')
    for pt in test_points:
        sec_z = 1 / np.cos(np.radians(pt['zenith']))
        fgcm_trans = new.interpolateAtmosphere(pmb=new.pmbElevation, **pt)
        direct = (emul.GetAllTransparencies(lam / 10.0, sec_z, pt['pwv'], pt['o3'], flagAerosols=False)
                  * aerosol_transmission(lam, sec_z, pt['tau'], pt['alpha']))
        diff = fgcm_trans - direct
        print(f'   secZ={sec_z:.2f} pwv={pt["pwv"]:4.1f} : max |diff| = {np.abs(diff).max():.4f}, '
              f'mean |diff| = {np.abs(diff).mean():.5f}')

    if reference is not None:
        ref = FgcmAtmosphereTable.initWithTableName(reference)
        ref.loadTable()
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, len(test_points), figsize=(5 * len(test_points), 7), sharex=True)
        print(f'\nnew table vs reference table ({os.path.basename(reference)}), same parameters, '
              'pressure = own PMBELEVATION :')
        for k, pt in enumerate(test_points):
            t_new = new.interpolateAtmosphere(lam=lam, pmb=new.pmbElevation, **pt)
            t_ref = ref.interpolateAtmosphere(lam=lam, pmb=ref.pmbElevation, **pt)
            sel = (t_ref > 0.05)
            ratio = np.where(sel, t_new / np.where(t_ref > 0, t_ref, np.nan), np.nan)
            print(f'   pwv={pt["pwv"]:4.1f} zenith={pt["zenith"]:5.1f} : median new/ref = '
                  f'{np.nanmedian(ratio):.4f}, rms = {np.nanstd(ratio):.4f}')
            axes[0, k].plot(lam / 10, t_ref, label='reference (MODTRAN)')
            axes[0, k].plot(lam / 10, t_new, label='new (getObsAtmo)', ls='--')
            axes[0, k].set_title(f'pwv={pt["pwv"]} mm, zenith={pt["zenith"]:.0f} deg')
            axes[1, k].plot(lam / 10, ratio)
            axes[1, k].set_ylim(0.8, 1.2)
            axes[1, k].set_xlabel('wavelength (nm)')
        axes[0, 0].set_ylabel('transmission')
        axes[0, 0].legend()
        axes[1, 0].set_ylabel('new / reference  (where reference > 0.05)')
        fig.tight_layout()
        if figure:
            fig.savefig(figure, bbox_inches='tight')
            print(f'figure : {figure}')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-o', '--output', default='fgcm_atm_obsatmo.fits')
    p.add_argument('--site', default='LSST', help='getObsAtmo site (default LSST)')
    p.add_argument('--clobber', action='store_true')
    p.add_argument('--check', action='store_true', help='read the table back with fgcm and test it')
    p.add_argument('--reference', default=None, help='reference fgcm table (e.g. fgcm_atm_lsst2.fits)')
    p.add_argument('--figure', default='fgcm_atm_obsatmo_vs_reference.png')
    # grids : defaults are those of the fgcm_atm_lsst2 table, except the pressure and zenith axes
    p.add_argument('--lambda-range', type=float, nargs=2, default=[3000.0, 11000.0], help='Angstrom')
    p.add_argument('--lambda-step', type=float, default=0.5, help='nm')
    p.add_argument('--pmb-range', type=float, nargs=2, default=[720.0, 750.0])
    p.add_argument('--pmb-steps', type=int, default=7)
    p.add_argument('--pwv-range', type=float, nargs=2, default=[0.1, 12.0])
    p.add_argument('--pwv-steps', type=int, default=21)
    p.add_argument('--o3-range', type=float, nargs=2, default=[220.0, 310.0])
    p.add_argument('--o3-steps', type=int, default=3)
    p.add_argument('--tau-range', type=float, nargs=2, default=[0.002, 0.35])
    p.add_argument('--tau-steps', type=int, default=11)
    p.add_argument('--alpha-range', type=float, nargs=2, default=[0.0, 2.0])
    p.add_argument('--alpha-steps', type=int, default=9)
    p.add_argument('--airmass-max', type=float, default=2.5, help='last airmass node (emulator limit is 2.6 '
                   'including the extra node)')
    p.add_argument('--zenith-steps', type=int, default=16)
    # standard atmosphere
    p.add_argument('--pmb-std', type=float, default=None, help='default : reference pressure of the site')
    p.add_argument('--pwv-std', type=float, default=3.0)
    p.add_argument('--o3-std', type=float, default=263.0)
    p.add_argument('--tau-std', type=float, default=0.03)
    p.add_argument('--alpha-std', type=float, default=1.0)
    p.add_argument('--airmass-std', type=float, default=1.2)
    args = p.parse_args(argv)

    pars, pwv_atm, o3_atm, o2_atm, ray_atm = build_table(args)
    write_table(args.output, pars, pwv_atm, o3_atm, o2_atm, ray_atm, args, clobber=args.clobber)
    print('shapes : PWVATM', pwv_atm.shape, 'O3ATM', o3_atm.shape, 'O2ATM', o2_atm.shape,
          'RAYATM', ray_atm.shape)
    print(f'PMBELEVATION = {pars["PMBELEVATION"]:.3f} hPa, PMBSTD = {pars["PMBSTD"]:.3f} hPa')
    if args.check:
        check_with_fgcm(args.output, args, reference=args.reference, figure=args.figure)


if __name__ == '__main__':
    sys.exit(main())
