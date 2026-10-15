#!/usr/bin/env python
"""
Split a list of Rubin exposure IDs (one per line, format YYYYMMDDNNNNN)
into several files grouped by year/month (default) or by ISO week.

Each output file contains a single comma-separated line, so it can be used as:

    export EXPOSURES=$(cat exposures_2025_05.txt)

and referenced in a BPS yaml as  exposure IN (${EXPOSURES}).

Usage:
    python split_exposures.py cosmos_selected20261006.txt
    python split_exposures.py cosmos_selected20261006.txt --by week -o splits
"""
import argparse
import datetime as dt
import os
import sys
from collections import defaultdict

# Linux limit for ONE environment string (MAX_ARG_STRLEN = 32 pages)
ENV_VAR_LIMIT = 131072


def parse_exposures(path):
    """Read exposure IDs, skipping blanks/comments, removing duplicates."""
    ids = set()
    with open(path) as f:
        for n, line in enumerate(f, 1):
            s = line.split("#")[0].strip()
            if not s:
                continue
            if not (s.isdigit() and len(s) == 13):
                print(f"Warning: line {n} ignored (unexpected format): {s!r}",
                      file=sys.stderr)
                continue
            ids.add(int(s))
    return sorted(ids)


def group_key(exp_id, by):
    """Return the group label of an exposure from its day_obs (first 8 digits)."""
    day_obs = str(exp_id)[:8]
    date = dt.datetime.strptime(day_obs, "%Y%m%d").date()
    if by == "month":
        return f"{date.year}_{date.month:02d}"
    iso = date.isocalendar()
    return f"{iso[0]}_W{iso[1]:02d}"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="text file with one exposure ID per line")
    p.add_argument("--by", choices=["month", "week"], default="month",
                   help="grouping (default: month)")
    p.add_argument("-o", "--outdir", default="exposure_lists",
                   help="output directory (default: exposure_lists)")
    args = p.parse_args()

    exposures = parse_exposures(args.input)
    groups = defaultdict(list)
    for e in exposures:
        groups[group_key(e, args.by)].append(e)

    os.makedirs(args.outdir, exist_ok=True)
    print(f"{len(exposures)} unique exposures -> {len(groups)} groups "
          f"(by {args.by}) in '{args.outdir}/'")
    print(f"{'group':<10}{'n_exp':>8}{'n_chars':>10}  ok_for_env_var")

    for key in sorted(groups):
        content = ",".join(str(e) for e in groups[key])
        fname = os.path.join(args.outdir, f"exposures_{key}.txt")
        with open(fname, "w") as f:
            f.write(content + "\n")
        ok = "yes" if len(content) < ENV_VAR_LIMIT else "NO (too long)"
        print(f"{key:<10}{len(groups[key]):>8}{len(content):>10}  {ok}")

    # Whole list in one line, to check if a single variable would be enough
    total = len(",".join(str(e) for e in exposures))
    print(f"\nWhole list as one string: {total} chars "
          f"(single-variable limit on Linux: {ENV_VAR_LIMIT})")


if __name__ == "__main__":
    main()
