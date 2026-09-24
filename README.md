MandiSense: Agri Price Forecasting + Spike Alerts

Status: work in progress. The data phase (Week 1) is done. Modelling has not started, so there are no model results yet. This README will only ever contain numbers produced by code in this repo.

Problem

Food processors, wholesalers and FPOs often do not see sudden mandi price spikes coming in onion, tomato and potato, so procurement timing ends up being a gut call. MandiSense aims to give a procurement manager:

A 7-day and 14-day ahead quantile forecast (P10 / P50 / P90) of the modal price.
A spike alert with a calibrated probability, plus an explanation of what drove it.
Planned scope
Commodities: potato first, then onion, then tomato if a usable source is found.
Models: LightGBM quantile forecasts, a spike classifier, SHAP explanations.
Validation: walk-forward only (expanding window with a gap). No random splits.
App: FastAPI (/forecast, /spike-risk, /explain, /health) and a Streamlit dashboard.
Deployment: Docker, with a live demo link once the app exists.

Build order: one commodity and 3 to 5 markets end to end first, then expand.

Data

Source for the current history: the Kaggle dump Indian Agricultural Mandi Prices (2023-2025), which is derived from Agmarknet (Ministry of Agriculture and Farmers Welfare). Please check the dataset's own licence before reusing it.

Daily ingestion from data.gov.in and a longer history from another source are planned but not done yet (API access is pending). See Limitations.

What the data checks found

Everything below was measured on the raw file with the scripts in this repo or the exploration behind them.

The file has 737,392 rows, 5 commodities, and dates from 2023-06-06 to 2025-06-11 (2.02 years). Dates are M/D/YYYY.
Potato: all 737 calendar days are present. 63 markets have data on at least 90% of days.
Onion: 90 calendar days are missing, in two blocks: 2024-06-07 to 2024-07-05 and 2024-12-07 to 2025-02-05.
Tomato: only 2023-06-06 to 2023-11-06 (154 days). Not usable for forecasting from this file.
One market (Pratapgarh) appears twice, under Uttar Pradesh and Rajasthan, with identical prices on all 688 days. It is treated as a duplicate and not used.
Several rows can exist per market per day (different variety or grade). To keep the series consistent, each market uses one fixed (variety, grade) pair: the one present on the most days. Days without that pair stay missing (nothing is filled at this stage).
Market key is state | district | market, since market names alone clash across states.
Panel v0

Potato, 5 Uttar Pradesh markets, chosen with measurable criteria (dominant variety-grade on at least 90% of days, no run of more than 10 identical prices, no daily change above 50%):

Market (district)	Days with data (of 737)
Ajuha (Prayagraj)	728
Tulsipur (Balrampur)	728
Madhoganj (Hardoi)	707
Rampur (Rampur)	698
Achnera (Agra)	691
EDA findings on the panel
Correlation: 7-day log price changes correlate between 0.60 and 0.73 for Achnera, Madhoganj, Ajuha and Rampur. Tulsipur is lower (0.37 to 0.42), so the 5 markets are related but not one signal.
Stationarity: price levels are non-stationary (ADF p between 0.448 and 0.683, KPSS p at its 0.01 floor). Log differences look stationary (ADF p about 0.000, KPSS p at its 0.10 cap).
Price regime: monthly median prices run from roughly 640 Rs/quintal (Jan 2024) to roughly 2430 Rs/quintal (Aug 2024), with one large rise and one large fall over the two years, moving across all five markets together.
Spike label (price(t+7) >= 1.25 x trailing 30-day median): 201 of 3,422 valid market-days (5.9%). 159 of those 201 fall in Feb-Mar 2024. Counted as separate windows across the markets there are only about three (Jun-Jul 2023, Feb-Mar 2024, Jun-Jul 2024).
Limitations (so far)
Only about 2 years of history. Yearly seasonality is seen once, and there are few independent spike events, so any spike classifier metric will rest on very few events. Every fold's result will be reported separately, together with how many spike events it contained.
The history ends in June 2025. A longer and more recent source is being explored.
Tomato has no usable history in this dump.
The panel covers 5 markets from a single state, and those markets move together to a large degree.
The spike label is relative to a trailing median. After a price trough it can fire on a rebound, which may not match what a buyer calls a spike.
Repo structure
src/        data and analysis scripts (build_panel.py, eda_potato.py)
api/        FastAPI app (planned)
app/        Streamlit dashboard (planned)
tests/      pytest tests (planned)
models/     trained models (planned)
notebooks/  exploration
data/       raw/ and processed/ are git-ignored, rebuilt by the scripts
Reproduce
bash
pip install -r requirements.txt
python src/build_panel.py    # downloads the Kaggle file and builds data/processed/potato_panel_v0.csv
python src/eda_potato.py     # prints the EDA above

The Kaggle download may need Kaggle credentials on your machine.

Roadmap
 Repo setup, data source checks, cleaning rules
 Potato panel v0 and EDA
 Longer history and daily ingestion
 Leakage-safe features, baselines (naive, seasonal naive, moving average, ETS/SARIMA)
 Walk-forward evaluation, LightGBM quantile model, spike classifier, calibration
 SHAP, error analysis
 FastAPI and Streamlit
 Procurement simulator (any result will be labelled as simulated in a backtest)
 Docker, deployment, demo video
Data credits

Agmarknet data via the Kaggle dump named above. If CEDA (Ashoka University) data is used later, CEDA will be credited in the app as its terms require.
