# ps158-reproduce

How has the wealth gap between American families with college-educated parents
and families whose parents have a high school education or less changed since
1989? This repo rebuilds and extends the Putnam (2015) wealth-gap figure through
the 2025 Survey of Consumer Finances.

## The figures

- `figures/networth_by_education_median.png`: **median** net worth of families
  with children, by education of the head of household, 1989–2025. This is the
  main figure, and it matches the dry-run chart. In 2025 the median was $626k for
  families headed by a college graduate and $72k for high school or less, a gap
  of 8.7 times (5.9 times in 1989).
- `figures/networth_by_education.png`: the same comparison using the **mean**
  ($2,291k vs. $269k in 2025, a gap of 8.5 times; 4.7 times in 1989).

Each figure has two panels: the two groups' net worth, and the ratio between them.

**Definitions**

- **Families with children:** at least one child of the reference person (or
  spouse/partner) lives at home (`KIDS > 0`).
- **Education:** that of the SCF reference person (the head of household).
  "High school or less" combines no diploma with a high school diploma or GED.
  "College" means a bachelor's degree or more.
- **Dollars:** all values are in 2025 dollars.

## Data

The data are the Federal Reserve Board's [Survey of Consumer Finances](https://www.federalreserve.gov/econres/scfindex.htm)
**summary extract public data**, one Stata file per survey (`scfp{YEAR}s.zip`),
for the 13 surveys from 1989 to 2025.

- **Inflation:** the Fed has already converted every survey to 2025 dollars, so
  the scripts don't adjust for inflation again.
- **Weights:** medians and means use the survey weight `WGT`. They are computed
  over all five of the survey's imputed copies of the data at once, which is how
  the Fed computes its own tables.
- **Check against the Fed:** for all families, the results match Table 4 of the
  Fed's historical tables (`scf2025_tables_public_real_historical.xlsx`) to
  within $5 (rounding only). The cut for families with children is not a table
  the Fed publishes.
- **Uncertainty:** the figures have no confidence intervals. For 2025, a 95%
  interval computed with the Fed's replicate weights is $535k–$716k for the
  college median and $50k–$94k for the high-school-or-less median.

## Rerun

You need Python 3 and an internet connection. Run these from the repo root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python get_data.py
.venv/bin/python plot.py
```

- `get_data.py` downloads the 13 extracts to `data/raw/` (about 430 MB, which git
  ignores) and writes `data/scf_networth_by_education.csv`. That CSV has the
  median, mean and share of families for each survey year, family type (all
  families or with children) and education group. Files that are already
  downloaded are reused.
- `plot.py` reads that CSV and writes both figures to `figures/`. To plot all
  families instead of families with children, change `FAMILIES` at the top of
  the script.
