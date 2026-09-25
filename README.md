MandiSense: Agri Price Forecasting + Spike Alerts
�
�
�
Load image
Load image
Quantile price forecasts and calibrated spike alerts for onion, tomato and potato mandi prices in India, built for procurement teams.
Project status. The data phase is complete and documented below. Modelling, the API and the dashboard are planned and not built yet. Every number in this README comes from code in this repo. Sections marked 🔜 are placeholders and contain no results.
Table of contents
Business problem
What the system will do
Architecture
Data
Methodology
Results
API
Dashboard
Repository structure
Tech stack
Quickstart
Configuration
Testing
Limitations
Roadmap
FAQ
Data credits and licence
Author
Food processors, wholesalers and FPOs buy onion, tomato and potato in bulk. Mandi prices can jump suddenly, and most buyers do not see it coming, so the timing of procurement ends up being a gut call.
Business problem
Target user: a procurement manager at a mid-size food processor who needs to decide when to buy over the next one to two weeks and wants to know why the system thinks a spike is coming.

What the system will do
Capability
Status
Clean, reproducible mandi price panel from Agmarknet data
✅ built
EDA: gaps, regimes, cross-market correlation, stationarity, spike-label episodes
✅ built
7-day and 14-day ahead quantile forecast (P10 / P50 / P90)
🔜 planned
Spike classifier with calibrated probabilities
🔜 planned
SHAP explanations for each alert
🔜 planned
FastAPI service and Streamlit dashboard
🔜 planned
Procurement simulator (results will always be labelled as a simulated backtest)
🔜 planned
Optional: short plain-language alert text, grounded in the SHAP drivers, template first
🔜 optional
Architecture
Target architecture (only the data box is implemented today):
flowchart LR
    A[Agmarknet mandi prices<br/>Kaggle history + daily ingestion] --> B[Cleaning and panel builder]
    B --> C[(SQLite)]
    C --> D[Leakage-safe feature builder]
    D --> E[LightGBM quantile forecaster]
    D --> F[Spike classifier + calibration]
    E --> G[FastAPI]
    F --> G
    F --> H[SHAP explainer]
    H --> G
    G --> I[Streamlit dashboard]
    J[GitHub Actions<br/>daily ingestion] --> B
    Data
Current source: the Kaggle dump Indian Agricultural Mandi Prices (2023-2025), which is derived from Agmarknet (Ministry of Agriculture and Farmers Welfare). Check the dataset's own licence before reusing it.
Planned additions: a longer and more recent history from another source, daily ingestion from data.gov.in, weather (Open-Meteo or NASA POWER) and a festival/season calendar. None of these are integrated yet.
What the data checks found
All numbers below were measured on the raw file.
Check
Finding
File size and range
737,392 rows, 5 commodities, 2023-06-06 to 2025-06-11 (2.02 years), dates in M/D/YYYY
Potato
All 737 calendar days present. 63 markets have data on at least 90% of days
Onion
90 calendar days missing, in two blocks: 2024-06-07 to 2024-07-05 and 2024-12-07 to 2025-02-05
Tomato
Only 2023-06-06 to 2023-11-06 (154 days). Not usable for forecasting from this file
Duplicates
Pratapgarh appears under Uttar Pradesh and Rajasthan with identical prices on all 688 days. Treated as a duplicate and excluded
Multiple rows per market-day
Different variety or grade rows exist. Each market uses one fixed (variety, grade) pair, the one present on the most days. Other days stay missing and nothing is filled at this stage
Market identity
A market is identified by state, district and market name together, because market names alone clash across states
Panel v0
Potato, 5 Uttar Pradesh markets, selected with measurable criteria: dominant variety-grade on at least 90% of days, no run of more than 10 identical prices, and no daily change above 50%.
Market (district)
Days with data (of 737)
Ajuha (Prayagraj)
728
Tulsipur (Balrampur)
728
Madhoganj (Hardoi)
707
Rampur (Rampur)
698
Achnera (Agra)
691
EDA findings on the panel
Cross-market correlation. 7-day log price changes correlate between 0.60 and 0.73 for Achnera, Madhoganj, Ajuha and Rampur. Tulsipur is lower (0.37 to 0.42). The markets are related but are not one signal.
Stationarity. Price levels are non-stationary (ADF p between 0.448 and 0.683, KPSS p at its 0.01 floor). Log differences look stationary (ADF p about 0.000, KPSS p at its 0.10 cap).
Price regime. Monthly median prices run from roughly 640 Rs/quintal (Jan 2024) to roughly 2430 Rs/quintal (Aug 2024), with one large rise and one large fall across the two years, moving across all five markets together.
Spike label (price(t+7) >= 1.25 x trailing 30-day median). 201 of 3,422 valid market-days (5.9%). 159 of those 201 fall in Feb-Mar 2024. Counted as distinct windows across the markets there are only about three: Jun-Jul 2023, Feb-Mar 2024 and Jun-Jul 2024.
Methodology
These are the design rules the modelling code will follow.
Validation
Walk-forward evaluation with an expanding window and a gap between train and test at least as long as the forecast horizon. No random splits.
Hyperparameter tuning (Optuna) on pinball loss, inside the training window only.
Each fold is reported separately, together with the number of spike events it contains.
Leakage rules
Every feature at time t uses information available up to t only.
Rolling statistics are computed on past data only.
price(t+7) is used only to build the label or target, never as a feature.
Missing days are handled explicitly and are not filled before the split.
Baselines: naive, seasonal naive, moving average, ETS / SARIMA.
Models: LightGBM (global quantile model), XGBoost or CatBoost for comparison, logistic regression for the spike task.
Metrics
Forecast: MAE, WAPE, MASE, pinball loss, interval coverage.
Spike: PR-AUC, recall at fixed precision, Brier score.
Business: a cost-based backtest, always labelled as simulated.
Statistics: ADF / KPSS, STL, ACF / PACF, rainfall to price cross-correlation, Diebold-Mariano test for forecast comparisons.
Results
🔜 No model results yet. This section will be filled from the evaluation code once it has been run. Planned tables:
Model
MAE
WAPE
MASE
Pinball loss
Coverage (P10-P90)
Naive
🔜
🔜
🔜
🔜
🔜
Seasonal naive
🔜
🔜
🔜
🔜
🔜
LightGBM quantile
🔜
🔜
🔜
🔜
🔜
Spike model
PR-AUC
Recall at fixed precision
Brier score
Spike events in test folds
Logistic regression
🔜
🔜
🔜
🔜
LightGBM (calibrated)
🔜
🔜
🔜
🔜
API
🔜 Planned contract. Field names may change when the service is implemented.
Endpoint
Method
Purpose
/health
GET
Service status
/forecast
POST
Quantile forecast (P10 / P50 / P90) for a market and horizon
/spike-risk
POST
Calibrated spike probability for a market
/explain
POST
SHAP drivers behind a forecast or alert
Dashboard
🔜 Planned Streamlit pages:
Market Overview
Forecast (fan chart)
Spike Alerts
Why? (SHAP)
Procurement Simulator
Model Report
Repository structure
src/         data and analysis scripts (build_panel.py, eda_potato.py)
api/         FastAPI service (planned)
app/         Streamlit dashboard (planned)
tests/       pytest tests (planned)
models/      trained models (planned)
notebooks/   exploration
data/        raw/ and processed/ are git-ignored and rebuilt by the scripts
Tech stack
Layer
Tools
Language
Python 3.10+
Data
Pandas, NumPy
Stats
statsmodels (ADF, KPSS, STL, ACF/PACF), SciPy
Modelling (planned)
LightGBM, scikit-learn, Optuna, SHAP
Serving (planned)
FastAPI, Pydantic, Uvicorn
Dashboard (planned)
Streamlit, Plotly
Storage (planned)
SQLite, optionally PostgreSQL
Ops (planned)
Docker, GitHub Actions (daily ingestion), pytest
Deployment (planned)
Streamlit Community Cloud or Hugging Face Spaces (UI), Render free tier (AP
Configuration
Environment variables (see .env.example), used once ingestion and the API are built:
Variable
Purpose
Required for
DATA_GOV_API_KEY
data.gov.in snapshot API, for daily ingestion
🔜 ingestion (not yet used)
CEDA_API_KEY
CEDA Agmarknet API, for longer history
🔜 ingestion (not yet used)
No keys are required to run build_panel.py or eda_potato.py today; both only read the public Kaggle dataset.
Testing
🔜 Planned. pytest will cover: leakage checks (no feature uses data from after its timestamp), the walk-forward split logic, and the panel-building rules (fixed variety/grade selection, duplicate-market detection). Run with:
Limitations
About 2 years of history. Yearly seasonality appears only once and there are very few independent spike events, so any spike metric will rest on a handful of events. Every fold will be reported separately.
The history ends in June 2025. A longer and more recent source is still being sorted out.
Tomato has no usable history in the current file.
The panel covers 5 markets from a single state, and those markets move together to a large degree.
The spike label is relative to a trailing median. After a price trough it can fire on a rebound, which may not match what a buyer would call a spike.
Roadmap
[x] Repo setup, data source checks, cleaning rules
[x] Potato panel v0 and EDA
[ ] Longer history and daily ingestion
[ ] Leakage-safe features and baselines
[ ] Walk-forward evaluation, LightGBM quantile model, spike classifier, calibration
[ ] SHAP and error analysis
[ ] FastAPI and Streamlit
[ ] Procurement simulator
[ ] Docker, deployment, demo video
FAQ
Why does this README say "work in progress" instead of showing results?
Because the modelling code has not been run yet. Every result in this repo will be produced by a script you can also run, so nothing here is a guess or a placeholder number dressed up as real.
Why only 5 markets and one commodity so far?
To get a correct, leakage-free pipeline working end to end first, then expand. The 5 markets and the selection rule are documented in Data.
Why is the spike-label rate so uneven across months?
The data checks found the spikes cluster into about three windows over two years (see EDA findings). That is a property of the data, not of the labelling threshold; the README documents it instead of hiding it.
Can I reuse the data or the code?
Check the Kaggle dataset's own licence for the data. The code in this repo is MIT-licensed (see Data credits and licence).
Data credits and licence
Agmarknet data, via the Kaggle dump named above.
If CEDA (Centre for Economic Data and Analysis, Ashoka University) data is used later, CEDA will be credited in the app as its terms require.
Code licence: MIT (add a LICENSE file to the repo).
Author
Navya Vashistha, GitHub @Navya2057. 
