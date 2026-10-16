"""Download the Survey of Consumer Finances summary extracts (1989-2025) and
compute median and mean family net worth by education of the head of
household, for all families and for families with children at home.

Source: Federal Reserve Board, SCF Summary Extract Public Data
(https://www.federalreserve.gov/econres/scfindex.htm). Each wave's extract,
scfp{YEAR}s.zip, holds rscfp{YEAR}.dta; all dollar variables in every wave are
inflation-adjusted to 2025 dollars by the Fed.

Education is EDCL, the education of the SCF "reference person" (the head of
household): 1 = no high school diploma, 2 = high school diploma or GED,
3 = some college or associate degree, 4 = bachelor's degree or more.

"With children" means KIDS > 0: at least one child of the reference person
(or spouse/partner) living in the household.

Medians and means pool the five implicates and use the weight WGT, which is how the Fed
computes the Bulletin tables; the results match Table 4 of the Fed's historical
tables to the dollar.

Writes data/scf_networth_by_education.csv.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = list(range(1989, 2026, 3))
URL = "https://www.federalreserve.gov/econres/files/scfp{year}s.zip"
RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/scf_networth_by_education.csv")

GROUPS = {
    "No high school diploma": [1],
    "High school diploma": [2],
    "High school or less": [1, 2],
    "Some college": [3],
    "College degree": [4],
    "All families": [1, 2, 3, 4],
}

FAMILIES = {
    "All families": lambda df: df,
    "With children": lambda df: df[df["kids"] > 0],
}


def download(year):
    """Return the path to rscfp{year}.dta, downloading it if needed."""
    dta = RAW_DIR / f"rscfp{year}.dta"
    if dta.exists():
        return dta
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {year} summary extract...")
    req = urllib.request.Request(URL.format(year=year), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        archive = zipfile.ZipFile(io.BytesIO(resp.read()))
    archive.extract(f"rscfp{year}.dta", RAW_DIR)
    return dta


def weighted_median(values, weights):
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cum = np.cumsum(weights)
    return values[np.searchsorted(cum, cum[-1] / 2)]


def summarize(year):
    df = pd.read_stata(download(year), columns=["wgt", "networth", "edcl", "kids"],
                       convert_categoricals=False)
    rows = []
    for families, select in FAMILIES.items():
        fam = select(df)
        total_weight = fam["wgt"].sum()
        for group, codes in GROUPS.items():
            sub = fam[fam["edcl"].isin(codes)]
            rows.append({
                "year": year,
                "families": families,
                "group": group,
                "median_networth": weighted_median(sub["networth"].to_numpy(), sub["wgt"].to_numpy()),
                "mean_networth": np.average(sub["networth"], weights=sub["wgt"]),
                "share_of_families": sub["wgt"].sum() / total_weight,  # within `families`
                "n_records": len(sub),  # five implicates per family
            })
    return rows


def main():
    rows = [row for year in YEARS for row in summarize(year)]
    out = pd.DataFrame(rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False, float_format="%.4f")
    print(f"Wrote {OUT_FILE} ({len(out)} rows)")


if __name__ == "__main__":
    main()
