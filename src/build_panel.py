"""Build the v0 potato panel (5 UP markets) from the Kaggle Agmarknet dump.

Rules (each one verified on the data in earlier steps):
- Dates are M/D/YYYY.
- Market key = state | district | market (market_name alone clashes).
- Rows with modal_price <= 0 are dropped.
- One fixed (variety, grade) pair per market: the one present on most days.
  Days where that pair is absent stay NaN (no filling at this stage).
- Chosen markets must not be exact duplicates of each other.
"""
import argparse
from pathlib import Path

import pandas as pd

KAGGLE_SLUG = "arjunyadav99/indian-agricultural-mandi-prices-20232025"
CSV_NAME = "Agriculture_price_dataset.csv"
COMMODITY = "Potato"
CHOSEN = [
    "Uttar Pradesh|prayagraj|Ajuha",
    "Uttar Pradesh|balrampur|Tulsipur",
    "Uttar Pradesh|hardoi|Madhoganj",
    "Uttar Pradesh|rampur|Rampur",
    "Uttar Pradesh|agra|Achnera",
]


def load_raw(csv_path=None):
    if csv_path is None:
        import kagglehub
        csv_path = Path(kagglehub.dataset_download(KAGGLE_SLUG)) / CSV_NAME
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["price_date"] = pd.to_datetime(df["price_date"], format="%m/%d/%Y")
    return df


def prepare(df, commodity=COMMODITY):
    df = df[(df["commodity"] == commodity) & (df["modal_price"] > 0)].copy()
    df["mkt_key"] = (df["state"].str.strip() + "|"
                     + df["district_name"].str.strip().str.lower() + "|"
                     + df["market_name"].str.strip())
    return df


def fixed_series(g, all_days):
    combo = (g.groupby(["variety", "grade"])["price_date"].nunique()
              .sort_values(ascending=False))
    variety, grade = combo.index[0]
    # same variety/grade can still repeat on a day, so median just collapses those
    s = (g[(g["variety"] == variety) & (g["grade"] == grade)]
           .groupby("price_date")["modal_price"].median().reindex(all_days))
    return s, f"{variety}/{grade}"


def build_panel(df, markets):
    all_days = pd.date_range(df["price_date"].min(), df["price_date"].max())
    frames, seen = [], {}
    for m in markets:
        g = df[df["mkt_key"] == m]
        if g.empty:
            raise ValueError(f"Market not found: {m}")
        s, combo = fixed_series(g, all_days)
        sig = tuple(s.fillna(-1).tolist())
        if sig in seen:
            raise ValueError(f"Duplicate series: {m} == {seen[sig]}")
        seen[sig] = m
        print(f"{m} | {combo} | obs={int(s.notna().sum())} | missing={int(s.isna().sum())}")
        frames.append(pd.DataFrame({"mkt_key": m, "date": all_days,
                                    "modal_price": s.values}))
    return pd.concat(frames, ignore_index=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=None,
                   help="Local CSV path (default: download from Kaggle)")
    p.add_argument("--out", default="data/processed/potato_panel_v0.csv")
    args = p.parse_args()

    df = prepare(load_raw(args.csv))
    print("Potato rows:", len(df), "| range:",
          df["price_date"].min().date(), "->", df["price_date"].max().date())
    panel = build_panel(df, CHOSEN)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(out, index=False)
    print("Saved:", out, "| rows:", len(panel))


if __name__ == "__main__":
    main()
