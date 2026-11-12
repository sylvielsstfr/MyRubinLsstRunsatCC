"""Build visit_to_exclude.txt from fgcm_visit_catalog_failures.csv (no duplicates).

The CSV is written by check_fgcm_visit_catalog.py, with one row per
(use_science, visit, stage-1 run). A visit therefore appears several times: once per
useScienceDetectors value and once per stage-1 run that contains it. Only the set of
distinct visit ids matters for the stage-2 exclusion.

Usage:
    python make_visit_to_exclude.py
    python make_visit_to_exclude.py --use-science False   # keep one useScienceDetectors value
    python make_visit_to_exclude.py --expr                # also write the data-query expression
"""
import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', default='fgcm_visit_catalog_failures.csv')
parser.add_argument('--output', default='visits_to_exclude.txt')
parser.add_argument('--use-science', choices=['True', 'False'], default=None,
                    help='keep only the failures obtained with this useScienceDetectors value '
                         '(default: union of both)')
parser.add_argument('--expr', action='store_true',
                    help="also write <output stem>_expr.txt containing 'exposure NOT IN (...)'")
args = parser.parse_args()

visits = set()
n_rows = 0
with open(args.input, newline='') as fh:
    for row in csv.DictReader(fh):
        n_rows += 1
        if args.use_science is not None and row['use_science'] != args.use_science:
            continue
        visits.add(int(row['visit']))

bad_visits = sorted(visits)
Path(args.output).write_text(''.join(f'{v}\n' for v in bad_visits))
print(f'{n_rows} rows read, {len(bad_visits)} distinct visits written to {args.output}')

expr = 'exposure NOT IN (' + ', '.join(str(v) for v in bad_visits) + ')'
if args.expr:
    expr_file = Path(args.output).with_name(Path(args.output).stem + '_expr.txt')
    expr_file.write_text(expr + '\n')
    print('expression written to', expr_file)
print(expr)
