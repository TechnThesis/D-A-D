# D-A-D: Data Analytics Dashboard 📊

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**D-A-D (Data Analytics Dashboard)** is an interactive analytics suite built with **Streamlit**, **Python**, **pandas**, and **Plotly**. It provides an end-to-end workflow for ingesting raw data, cleaning datasets with audited transformations, computing key statistical metrics, rendering filterable interactive visualizations, and exporting executive dossiers.

---

## 🌟 Key Capabilities

### 1. Data Ingestion & Preloaded Datasets
- **Multi-Format Ingestion**: Upload datasets via CSV, Excel (`.xlsx`, `.xls`), TSV, JSON, or Parquet.
- **Built-in Curated Datasets**: Instantly test features with pre-configured datasets:
  - *Retail Sales & Transactions* (250 orders with regional, category, revenue, and profit metrics)
  - *SaaS Growth & Churn Metrics* (180 accounts with MRR, usage hours, support tickets, and NPS)
  - *HR Workforce & Attrition* (160 employees across roles, tenure, compensation, and retention)

### 2. Comprehensive Data Cleaning Studio
- **Missing Value Remediation**: Impute null values using Mean, Median, Mode, Forward Fill, Backward Fill, or custom constants, or drop null records.
- **Deduplication Engine**: Identify duplicate rows across all or targeted column subsets.
- **Data Type Casting**: Re-cast features to `datetime`, `numeric`, `integer`, `string`, `category`, or `boolean`.
- **Outlier Detection & Remediation**:
  - Detect anomalies using **IQR (Interquartile Range)** or **Z-Score (>3σ)**.
  - Choose between Winsorizing (clipping to boundaries), removing outlier rows, or flagging them with a boolean indicator.
- **Text & String Standardization**: Whitespace trimming, uppercase/lowercase/title-case conversion, and special character sanitization.
- **Feature Engineering**: Column renaming, column removal, date component extraction (Year, Month, Quarter, Day of Week), and arithmetic feature creation.
- **Audit History & Snapshot Reset**: Complete chronological audit trail tracking every transformation with one-click rollback to original data.

### 3. Key Metrics & Statistical Exploratory Data Analysis (EDA)
- **High-Level KPI Cards**: Active record count, total attributes, missing cell count & percentage, duplicate counts, and memory footprint.
- **Numerical Summary Statistics**: Mean, Standard Deviation, Min, 25%, Median (50%), 75%, Max, IQR, Skewness, and Kurtosis.
- **Categorical Breakdown**: Cardinality, mode, frequency counts, and top category distribution bars.
- **Correlation Engine**: Pearson and Spearman correlation heatmaps with automated ranking of strongest correlated feature pairs.
- **Multi-Dimensional Group-By**: Interactive pivot aggregations (`sum`, `mean`, `median`, `count`, `min`, `max`, `std`).

### 4. Interactive Filterable Chart Studio (Plotly)
- **Global Reactive Filtering**: Slice and dice charts in real-time by categorical multi-select, numeric range sliders, and date interval selectors.
- **Diverse Plotly Visualizations**:
  - Scatter Plots with optional OLS trendlines, color dimensions, and bubble sizes
  - Line & Time-Series Charts with markers
  - Grouped, stacked, and relative Bar Charts
  - Histograms with KDE and marginal box/violin plots
  - Box & Violin plots for variance analysis
  - Donut & Pie charts with custom hole sizes
  - Hierarchical Treemaps
- **Interactive Chart Export**: Download rendered figures as self-contained standalone HTML or SVG/PNG images.

### 5. Multi-Asset Exportable Reporting
- **Cleaned Data Export (CSV)**: UTF-8 encoded cleaned table ready for machine learning pipelines.
- **Multi-Tab Excel Workbook (.xlsx)**: Formatted spreadsheet including both cleaned data and summary statistics sheets.
- **Executive HTML Dossier**: Downloadable, publication-ready HTML dossier with key metrics, health overview, descriptive statistics table, and transformation audit trail.
- **Summary Statistics CSV**: Export descriptive metrics for presentation decks and documentation.

---

## 🚀 Instant Deployment on Streamlit Cloud

You can deploy this dashboard directly from GitHub to Streamlit Cloud in less than 2 minutes:

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **"New app"**.
3. Select this repository: `TechnThesis/D-A-D`.
4. Set **Branch** to `main`.
5. Set **Main file path** to `app.py`.
6. Click **"Deploy!"**.

Streamlit Cloud will automatically detect `requirements.txt` and launch your live application!

---

## 💻 Local Development Setup

To run the dashboard locally on your machine:

```bash
# 1. Clone the repository
git clone https://github.com/TechnThesis/D-A-D.git
cd D-A-D

# 2. (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit dashboard
streamlit run app.py
```

The application will start and open automatically in your browser at `http://localhost:8501`.

---

## 📁 Repository Structure

```
├── .streamlit/
│   └── config.toml          # Streamlit theme & UI styling configurations
├── sample_data/             # Preloaded demonstration datasets
│   ├── sales_data.csv       # Retail sales, orders, discounts & profits
│   ├── saas_metrics.csv     # SaaS MRR, subscriptions, churn & usage
│   └── hr_attrition.csv     # Workforce demographics, salary & retention
├── app.py                   # Main Streamlit application codebase
├── requirements.txt         # Production Python package requirements
├── .gitignore               # Git ignore rules for Python artifacts
└── README.md                # Project documentation and deployment guide
```

---

## 📄 License

This project is licensed under the MIT License - feel free to use and adapt it for personal and enterprise analytics.
