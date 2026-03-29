# EasyAnalytics

A no-code data analysis web app built with Streamlit. Upload a CSV or Excel file and get instant statistical summaries, interactive charts, ML-powered insights, and exportable HTML reports — no Python knowledge required.

---

## What it does

| Page | What you get |
|---|---|
| **Upload** | Drag-and-drop CSV / Excel, or load a built-in sample dataset |
| **Explore** | Data overview, column stats, missing value handling, auto-generated insights |
| **Analyze** | Descriptive stats, distributions, correlations, time series, group analysis, outlier detection, clustering (KMeans + PCA), and prediction (Random Forest) |
| **Report** | Build a custom report by adding text, charts, and analysis results — export as HTML |

---

## Quick start

The easiest way is to use the provided shell script:

```bash
bash run.sh
```

That's it. The script creates a virtual environment, installs dependencies, and launches the app.

---

## Manual setup

If you prefer to do it yourself:

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Requirements

- Python 3.9+
- pip

All Python dependencies are listed in `requirements.txt` and installed automatically by `run.sh`.

---

## Project structure

```
.
├── app.py                  # Entry point and page router
├── run.sh                  # One-command launcher
├── requirements.txt
├── components/
│   ├── header.py           # Page config and top bar
│   ├── sidebar.py          # Navigation and file upload
│   ├── explore.py          # Data exploration tabs
│   ├── analyze.py          # Analysis page and renderers
│   ├── report.py           # Report builder UI
│   └── report_utils.py     # Chart helpers and HTML export
└── utils/
    ├── data_processing.py  # Load, summarize, and clean data
    ├── analysis.py         # Statistical and ML analysis functions
    └── visualization.py    # Plotly chart builders
```

---

## Supported file formats

- CSV (configurable delimiter and encoding)
- Excel (`.xlsx`, `.xls`, configurable sheet name)

---

## Analysis types

- **Descriptive statistics** — mean, median, std, skewness, kurtosis
- **Distribution analysis** — histograms for numeric, bar charts for categorical
- **Correlation analysis** — Pearson / Spearman / Kendall heatmaps
- **Time series analysis** — trend lines, daily / weekly / monthly aggregations
- **Group analysis** — aggregate a numeric column by any categorical column
- **Outlier analysis** — IQR and Z-score methods with visual highlighting
- **Missing values analysis** — per-column breakdown with fill / drop options
- **Clustering** — KMeans with PCA visualization
- **Prediction** — Random Forest regression or classification with feature importance

---

## License

MIT
