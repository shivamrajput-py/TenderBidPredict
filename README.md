# TenderBidPredict

TenderBidPredict is a Streamlit-based analytics project for exploring contractor performance in public tender datasets and training machine learning models on bid pricing patterns. The project is designed as a clean, portfolio-ready showcase of data application development, interactive analytics, and practical ML workflow design.

## Highlights

- Interactive contractor intelligence dashboard built with Streamlit
- Search-driven tender profile exploration with polished visual analytics
- District, department, pricing, and trend analysis in a single interface
- Reproducible machine learning training pipeline with model comparison
- Lightweight local-first setup with CSV, JSON, and joblib artifacts
- Portfolio-friendly code structure with clear project documentation

## Project Modules

### 1. Contractor Intelligence Dashboard

The main application is powered by [`mainStreamlit.py`](./mainStreamlit.py). It provides:

- Contractor search with fuzzy matching
- Executive-style overview metrics
- District-level tender distribution
- Department concentration analysis
- Win activity trend view over time
- Tabular recent tender records for deeper inspection

This dashboard is ideal for demonstrating:

- Streamlit UI design
- Data storytelling
- Business-facing analytics workflows
- Local dataset exploration without backend complexity

### 2. Machine Learning Training Pipeline

The training workflow is implemented in [`prep_model.py`](./prep_model.py). It now includes:

- Dataset loading and validation
- Feature-target separation
- Preprocessing with imputers, scaling, and categorical encoding
- Multiple candidate regressors
- Cross-validation-based model comparison
- Holdout evaluation using MAE, RMSE, and R²
- Automatic persistence of the best model and training report

Candidate models currently evaluated:

- Elastic Net Regression
- Random Forest Regressor
- Extra Trees Regressor

This makes the ML component more representative of a production-style experimentation pipeline instead of a single-script training demo.

### 3. Tender Filing Utility

[`TenderFilling.py`](./TenderFilling.py) contains a Streamlit-based tender document collection workflow powered by Selenium for scraping tender document requirements from the official portal and capturing uploads locally.

### 4. Data Assets

The repository includes working datasets and pre-trained artifacts used for analytics and ML experimentation:

- [`BIDDERS_PROFILE_INSIGHTS_15TO24.json`](./BIDDERS_PROFILE_INSIGHTS_15TO24.json)
- [`ElectricalWorks.csv`](./ElectricalWorks.csv)
- [`bridges.csv`](./bridges.csv)
- Existing `.pkl` model artifacts

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly Express
- scikit-learn
- Joblib
- Selenium
- YAML / JSON / CSV

## Repository Structure

```text
BidpredictStreamlit/
├── .devcontainer/              # Dev container setup for VS Code / Codespaces
├── .streamlit/                 # Streamlit-related configuration
├── BIDDERS_PROFILE_INSIGHTS_15TO24.json
├── ElectricalWorks.csv
├── bridges.csv
├── mainStreamlit.py            # Main analytics dashboard
├── prep_model.py               # ML training pipeline
├── TenderFilling.py            # Tender filing workflow
├── shortenTHEJSON.py           # JSON optimization helper
├── style.css                   # Dashboard styling
├── requirements.txt            # Python dependencies
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd BidpredictStreamlit
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running The Dashboard

```bash
streamlit run mainStreamlit.py
```

The app opens a contractor intelligence dashboard where you can search a bidder and review performance insights through metrics, charts, and tender tables.

## Training The ML Model

```bash
python prep_model.py
```

Running the training pipeline will:

- evaluate multiple regression models
- select the strongest candidate on the holdout split
- save the trained model to `artifacts/best_bid_estimator.pkl`
- save a structured report to `artifacts/training_report.json`

## Design Goals

This project was structured to emphasize:

- clarity over unnecessary framework complexity
- practical analytics for real tender data
- readable Python for recruiters and collaborators
- a presentable Streamlit UI suitable for demos and GitHub portfolios
- reproducible ML experimentation with saved outputs

## Use Cases

TenderBidPredict can be used as a base for:

- contractor profiling
- bid intelligence dashboards
- procurement analytics
- estimating bid-value trends
- internal research tools for tender consulting teams

## Development Notes

- The project supports a Dev Container workflow through [`.devcontainer/devcontainer.json`](./.devcontainer/devcontainer.json)
- Styling is customized through [`style.css`](./style.css)
- Streamlit configuration is kept under [`.streamlit`](./.streamlit)

## Why This Project Stands Out

This repository combines three strong portfolio signals in one codebase:

1. Interactive analytics application development
2. Real-world data preprocessing and visualization
3. Structured machine learning experimentation and artifact generation

It is intentionally lightweight to run locally while still showing end-to-end ownership across UI, data work, and ML engineering.
