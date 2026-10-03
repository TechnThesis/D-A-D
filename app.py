"""
D-A-D: Data Analytics Dashboard
An interactive dashboard that cleans datasets, computes key metrics, and renders filterable charts and exportable reports.
Built with Streamlit, Python, pandas, and Plotly.
"""

import io
import os
import json
import base64
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="D-A-D | Data Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished dashboard typography and cards
st.markdown("""
<style>
    /* Metric Card styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-subtext {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 2px;
    }
    .report-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 24px;
    }
    .report-banner h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 1.8rem;
    }
    .report-banner p {
        color: #94a3b8;
        margin: 6px 0 0 0;
        font-size: 0.95rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# CACHED DATA LOADING HELPERS
# ==========================================
@st.cache_data(show_spinner=False)
def load_sample_file(path: str) -> pd.DataFrame:
    """Load built-in sample CSV file."""
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Parse user-uploaded file across supported formats."""
    file_name = uploaded_file.name.lower()
    try:
        if file_name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif file_name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        elif file_name.endswith('.tsv'):
            return pd.read_csv(uploaded_file, sep='\t')
        elif file_name.endswith('.json'):
            return pd.read_json(uploaded_file)
        elif file_name.endswith('.parquet'):
            return pd.read_parquet(uploaded_file)
        else:
            # Fallback attempt as CSV
            return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return pd.DataFrame()


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'dataset_name' not in st.session_state:
    st.session_state.dataset_name = "Untitled Dataset"
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []


def set_dataset(df: pd.DataFrame, name: str):
    """Set the active dataset in session state."""
    st.session_state.original_df = df.copy()
    st.session_state.cleaned_df = df.copy()
    st.session_state.dataset_name = name
    st.session_state.audit_log = [
        f"Initial dataset loaded: '{name}' ({df.shape[0]} rows, {df.shape[1]} columns)"
    ]


# ==========================================
# SIDEBAR: DATA INGESTION & GLOBAL CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("### 📊 D-A-D Studio")
    st.caption("Data Analytics & Automated Cleaning Engine")

    data_source_mode = st.radio(
        "Data Ingestion Source",
        ["Sample Datasets", "Upload File"],
        index=0,
        horizontal=True
    )

    if data_source_mode == "Sample Datasets":
        sample_choice = st.selectbox(
            "Choose a Preloaded Dataset",
            [
                "Retail Sales & Transactions",
                "SaaS Growth & Churn Metrics",
                "HR Workforce & Attrition"
            ]
        )

        sample_paths = {
            "Retail Sales & Transactions": "sample_data/sales_data.csv",
            "SaaS Growth & Churn Metrics": "sample_data/saas_metrics.csv",
            "HR Workforce & Attrition": "sample_data/hr_attrition.csv"
        }

        if st.button("Load Dataset", type="primary", use_container_width=True):
            target_path = sample_paths[sample_choice]
            # Try relative path or applet path
            if not os.path.exists(target_path):
                target_path = os.path.join(os.path.dirname(__file__), target_path)
            loaded = load_sample_file(target_path)
            if not loaded.empty:
                set_dataset(loaded, sample_choice)
                st.success(f"Loaded {sample_choice} ({len(loaded)} rows)")
            else:
                st.error("Sample dataset file could not be read.")

    else:
        uploaded_file = st.file_uploader(
            "Upload your dataset (CSV, XLSX, TSV, JSON, Parquet)",
            type=["csv", "xlsx", "xls", "tsv", "json", "parquet"]
        )
        if uploaded_file is not None:
            if st.button("Process Uploaded File", type="primary", use_container_width=True):
                df = parse_uploaded_file(uploaded_file)
                if not df.empty:
                    set_dataset(df, uploaded_file.name)
                    st.success(f"Loaded {uploaded_file.name} ({len(df)} rows)")

    st.markdown("---")

    # Global Reset & Status
    if st.session_state.cleaned_df is not None:
        st.markdown(f"**Current:** {st.session_state.dataset_name}")
        st.caption(f"{st.session_state.cleaned_df.shape[0]:,} rows · {st.session_state.cleaned_df.shape[1]} cols")
        
        if st.button("↺ Reset to Original Data", use_container_width=True):
            st.session_state.cleaned_df = st.session_state.original_df.copy()
            st.session_state.audit_log.append("User reset data back to original state.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 Deployment Info")
    st.caption("Push ready for Streamlit Cloud via TechnThesis/D-A-D repository.")


# Check if dataset is loaded; if not, auto-load default sample
if st.session_state.cleaned_df is None:
    default_path = "sample_data/sales_data.csv"
    if not os.path.exists(default_path):
        default_path = os.path.join(os.path.dirname(__file__), default_path)
    if os.path.exists(default_path):
        default_df = pd.read_csv(default_path)
        set_dataset(default_df, "Retail Sales & Transactions")


df = st.session_state.cleaned_df

# ==========================================
# TOP HEADER BANNER
# ==========================================
st.markdown(f"""
<div class="report-banner">
    <h1>Data Analytics Dashboard</h1>
    <p>Comprehensive dataset cleaning, statistical metrics computation, filterable interactive visualizations, and exportable reports.</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5 MAIN WORKSPACE TABS
# ==========================================
tab_overview, tab_cleaning, tab_metrics, tab_charts, tab_export = st.tabs([
    "1. Overview & Health",
    "2. Data Cleaning Studio",
    "3. Key Metrics & EDA",
    "4. Interactive Chart Studio",
    "5. Exportable Reports"
])


# ==============================================================================
# TAB 1: OVERVIEW & HEALTH AUDIT
# ==============================================================================
with tab_overview:
    st.subheader("Dataset Health & Structural Profile")

    # KPI summary cards
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    total_nulls = int(df.isnull().sum().sum())
    null_percentage = (total_nulls / total_cells * 100) if total_cells > 0 else 0
    duplicate_rows = int(df.duplicated().sum())
    memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total_rows:,}</div>
            <div class="metric-subtext">Rows in dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Attributes</div>
            <div class="metric-value">{total_cols}</div>
            <div class="metric-subtext">Columns/Features</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Missing Values</div>
            <div class="metric-value">{total_nulls:,}</div>
            <div class="metric-subtext">{null_percentage:.2f}% of all cells</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Duplicates</div>
            <div class="metric-value">{duplicate_rows:,}</div>
            <div class="metric-subtext">Identical rows</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Memory Footprint</div>
            <div class="metric-value">{memory_usage_mb:.2f} MB</div>
            <div class="metric-subtext">Deep RAM usage</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Column Inventory & Missing Value Audit")
    
    col_audit = []
    for col in df.columns:
        n_missing = int(df[col].isnull().sum())
        p_missing = round(n_missing / total_rows * 100, 2) if total_rows > 0 else 0
        n_unique = int(df[col].nunique(dropna=True))
        dtype_str = str(df[col].dtype)
        col_audit.append({
            "Column Name": col,
            "Data Type": dtype_str,
            "Non-Null Count": total_rows - n_missing,
            "Missing Count": n_missing,
            "Missing Rate (%)": p_missing,
            "Unique Values": n_unique
        })
    
    audit_df = pd.DataFrame(col_audit)

    c_audit_table, c_audit_chart = st.columns([3, 2])
    with c_audit_table:
        st.dataframe(audit_df, use_container_width=True, height=280)

    with c_audit_chart:
        missing_subset = audit_df[audit_df["Missing Count"] > 0]
        if not missing_subset.empty:
            fig_missing = px.bar(
                missing_subset,
                x="Column Name",
                y="Missing Rate (%)",
                text="Missing Count",
                title="Missing Values by Feature",
                color_discrete_sequence=["#ef4444"]
            )
            fig_missing.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=280)
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("✓ Excellent data health: Zero missing values detected in any column!")

    st.markdown("#### Live Data Preview")
    preview_limit = st.slider("Preview Rows", min_value=5, max_value=min(100, total_rows), value=10, step=5)
    st.dataframe(df.head(preview_limit), use_container_width=True)


# ==============================================================================
# TAB 2: DATA CLEANING STUDIO
# ==============================================================================
with tab_cleaning:
    st.subheader("Data Cleaning & Transformation Studio")
    st.write("Perform targeted cleaning operations. Each modification updates the dataset and logs into the audit history.")

    clean_tabs = st.tabs([
        "Missing Values",
        "Deduplication",
        "Type Casting",
        "Outlier Detection",
        "Text Cleaning",
        "Feature Engineering",
        "Audit Log"
    ])

    # 1. MISSING VALUES
    with clean_tabs[0]:
        st.markdown("##### Handle Missing & Null Values")
        null_cols = [c for c in df.columns if df[c].isnull().sum() > 0]
        
        if not null_cols:
            st.info("No missing values found in the active dataset.")
        else:
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                selected_null_col = st.selectbox("Target Column with Nulls", null_cols)
                curr_nulls = int(df[selected_null_col].isnull().sum())
                st.caption(f"Current nulls: {curr_nulls} ({curr_nulls/len(df)*100:.1f}%)")
            with c2:
                is_numeric = pd.api.types.is_numeric_dtype(df[selected_null_col])
                options = ["Drop Rows with Null", "Forward Fill", "Backward Fill", "Fill Constant"]
                if is_numeric:
                    options = ["Fill with Mean", "Fill with Median", "Fill with Mode"] + options
                else:
                    options = ["Fill with Mode"] + options
                
                impute_strategy = st.selectbox("Imputation Strategy", options)
                constant_val = None
                if impute_strategy == "Fill Constant":
                    constant_val = st.text_input("Constant Value to Fill", value="Unknown")

            with c3:
                st.write("")
                st.write("")
                if st.button("Apply Missing Value Fix", type="primary"):
                    if impute_strategy == "Drop Rows with Null":
                        st.session_state.cleaned_df = df.dropna(subset=[selected_null_col]).copy()
                        msg = f"Dropped rows with nulls in '{selected_null_col}' (-{curr_nulls} rows)"
                    elif impute_strategy == "Fill with Mean":
                        val = df[selected_null_col].mean()
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].fillna(val)
                        msg = f"Imputed nulls in '{selected_null_col}' with Mean ({val:.2f})"
                    elif impute_strategy == "Fill with Median":
                        val = df[selected_null_col].median()
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].fillna(val)
                        msg = f"Imputed nulls in '{selected_null_col}' with Median ({val:.2f})"
                    elif impute_strategy == "Fill with Mode":
                        val = df[selected_null_col].mode()[0]
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].fillna(val)
                        msg = f"Imputed nulls in '{selected_null_col}' with Mode ('{val}')"
                    elif impute_strategy == "Forward Fill":
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].ffill()
                        msg = f"Forward filled nulls in '{selected_null_col}'"
                    elif impute_strategy == "Backward Fill":
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].bfill()
                        msg = f"Backward filled nulls in '{selected_null_col}'"
                    elif impute_strategy == "Fill Constant":
                        fill_v = constant_val
                        if is_numeric:
                            try:
                                fill_v = float(constant_val)
                            except ValueError:
                                pass
                        st.session_state.cleaned_df[selected_null_col] = df[selected_null_col].fillna(fill_v)
                        msg = f"Filled nulls in '{selected_null_col}' with constant '{fill_v}'"
                    
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()

            # Bulk drop nulls button
            st.markdown("---")
            c_bulk1, c_bulk2 = st.columns([3, 1])
            with c_bulk1:
                st.caption("Drop any row containing missing values across all columns.")
            with c_bulk2:
                if st.button("Drop All Rows with Any Null"):
                    before_len = len(df)
                    st.session_state.cleaned_df = df.dropna().copy()
                    diff = before_len - len(st.session_state.cleaned_df)
                    msg = f"Dropped all rows with any missing values (-{diff} rows)"
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()

    # 2. DEDUPLICATION
    with clean_tabs[1]:
        st.markdown("##### Remove Duplicate Records")
        n_dups = int(df.duplicated().sum())
        st.write(f"Detected **{n_dups}** exact duplicate rows across all columns.")
        
        c_dup1, c_dup2 = st.columns([3, 1])
        with c_dup1:
            subset_cols = st.multiselect("Columns to check for uniqueness (leave blank for all columns)", df.columns.tolist())
        with c_dup2:
            st.write("")
            st.write("")
            keep_rule = st.selectbox("Keep occurrence", ["first", "last"])

        if st.button("Remove Duplicates", type="primary"):
            subset = subset_cols if subset_cols else None
            before = len(df)
            st.session_state.cleaned_df = df.drop_duplicates(subset=subset, keep=keep_rule).copy()
            removed = before - len(st.session_state.cleaned_df)
            cols_note = f"on columns {subset}" if subset else "across all columns"
            msg = f"Removed {removed} duplicate rows {cols_note} (kept {keep_rule})"
            st.session_state.audit_log.append(msg)
            st.success(msg)
            st.rerun()

    # 3. TYPE CASTING
    with clean_tabs[2]:
        st.markdown("##### Cast Feature Data Types")
        c_tc1, c_tc2, c_tc3 = st.columns([2, 2, 2])
        with c_tc1:
            cast_col = st.selectbox("Select Column to Recast", df.columns.tolist(), key="cast_col_select")
            st.caption(f"Current type: `{df[cast_col].dtype}`")
        with c_tc2:
            target_type = st.selectbox("Target Type", ["datetime", "numeric (float)", "integer", "string", "category", "boolean"])
        with c_tc3:
            st.write("")
            st.write("")
            if st.button("Convert Type", type="primary"):
                try:
                    if target_type == "datetime":
                        st.session_state.cleaned_df[cast_col] = pd.to_datetime(df[cast_col], errors='coerce')
                    elif target_type == "numeric (float)":
                        st.session_state.cleaned_df[cast_col] = pd.to_numeric(df[cast_col], errors='coerce')
                    elif target_type == "integer":
                        st.session_state.cleaned_df[cast_col] = pd.to_numeric(df[cast_col], errors='coerce').fillna(0).astype(int)
                    elif target_type == "string":
                        st.session_state.cleaned_df[cast_col] = df[cast_col].astype(str)
                    elif target_type == "category":
                        st.session_state.cleaned_df[cast_col] = df[cast_col].astype('category')
                    elif target_type == "boolean":
                        st.session_state.cleaned_df[cast_col] = df[cast_col].astype(bool)

                    msg = f"Converted column '{cast_col}' to {target_type}"
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()
                except Exception as e:
                    st.error(f"Conversion failed: {e}")

    # 4. OUTLIER DETECTION
    with clean_tabs[3]:
        st.markdown("##### Outlier Detection & Treatment (IQR / Z-Score)")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not num_cols:
            st.warning("No numeric columns available for outlier detection.")
        else:
            c_o1, c_o2, c_o3 = st.columns([2, 2, 2])
            with c_o1:
                target_num = st.selectbox("Select Numeric Attribute", num_cols, key="outlier_num_col")
            with c_o2:
                method = st.selectbox("Detection Method", ["IQR (Interquartile Range)", "Z-Score (> 3 Std Dev)"])
            with c_o3:
                action = st.selectbox("Action", ["Clip Outliers (Winsorize)", "Remove Outlier Rows", "Flag with New Column"])

            # Compute boundaries
            col_series = df[target_num].dropna()
            if method.startswith("IQR"):
                q25 = col_series.quantile(0.25)
                q75 = col_series.quantile(0.75)
                iqr = q75 - q25
                lower_b = q25 - 1.5 * iqr
                upper_b = q75 + 1.5 * iqr
                outliers = df[(df[target_num] < lower_b) | (df[target_num] > upper_b)]
            else:
                mean = col_series.mean()
                std = col_series.std()
                lower_b = mean - 3 * std
                upper_b = mean + 3 * std
                outliers = df[(df[target_num] < lower_b) | (df[target_num] > upper_b)]

            st.caption(f"Detected **{len(outliers)}** outliers outside bounds [{lower_b:.2f}, {upper_b:.2f}].")

            if st.button("Execute Outlier Action", type="primary"):
                if action == "Clip Outliers (Winsorize)":
                    st.session_state.cleaned_df[target_num] = df[target_num].clip(lower=lower_b, upper=upper_b)
                    msg = f"Clipped {len(outliers)} outliers in '{target_num}' to [{lower_b:.2f}, {upper_b:.2f}]"
                elif action == "Remove Outlier Rows":
                    st.session_state.cleaned_df = df[(df[target_num] >= lower_b) & (df[target_num] <= upper_b)].copy()
                    msg = f"Removed {len(outliers)} outlier rows in '{target_num}'"
                elif action == "Flag with New Column":
                    flag_col = f"{target_num}_is_outlier"
                    st.session_state.cleaned_df[flag_col] = (df[target_num] < lower_b) | (df[target_num] > upper_b)
                    msg = f"Added flag column '{flag_col}' for {len(outliers)} outliers"

                st.session_state.audit_log.append(msg)
                st.success(msg)
                st.rerun()

    # 5. TEXT CLEANING
    with clean_tabs[4]:
        st.markdown("##### Clean Text & Categorical Strings")
        str_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if not str_cols:
            st.warning("No string/categorical columns found.")
        else:
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                text_col = st.selectbox("Select String Column", str_cols, key="text_col_select")
                text_action = st.selectbox(
                    "String Operation",
                    ["Trim Whitespace", "Convert to Lowercase", "Convert to UPPERCASE", "Convert to Title Case", "Remove Special Characters"]
                )
            with c_t2:
                st.write("")
                st.write("")
                if st.button("Apply Text Cleaning", type="primary"):
                    series = df[text_col].astype(str)
                    if text_action == "Trim Whitespace":
                        st.session_state.cleaned_df[text_col] = series.str.strip()
                    elif text_action == "Convert to Lowercase":
                        st.session_state.cleaned_df[text_col] = series.str.lower()
                    elif text_action == "Convert to UPPERCASE":
                        st.session_state.cleaned_df[text_col] = series.str.upper()
                    elif text_action == "Convert to Title Case":
                        st.session_state.cleaned_df[text_col] = series.str.title()
                    elif text_action == "Remove Special Characters":
                        st.session_state.cleaned_df[text_col] = series.str.replace(r'[^A-Za-z0-9\s]+', '', regex=True)

                    msg = f"Applied '{text_action}' on column '{text_col}'"
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()

    # 6. FEATURE ENGINEERING & COLUMNS
    with clean_tabs[5]:
        st.markdown("##### Column Operations & Derived Features")
        f_type = st.radio("Operation Type", ["Math Transformation", "Date Part Extraction", "Drop Columns", "Rename Column"], horizontal=True)

        if f_type == "Math Transformation":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(num_cols) >= 2:
                c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                with c_m1:
                    col_a = st.selectbox("Operand A", num_cols, key="math_a")
                with c_m2:
                    op = st.selectbox("Operator", ["+", "-", "*", "/"])
                with c_m3:
                    col_b = st.selectbox("Operand B", num_cols, key="math_b")
                with c_m4:
                    new_col_name = st.text_input("New Column Name", value=f"{col_a}_{op}_{col_b}")
                
                if st.button("Calculate Feature", type="primary"):
                    if op == "+":
                        st.session_state.cleaned_df[new_col_name] = df[col_a] + df[col_b]
                    elif op == "-":
                        st.session_state.cleaned_df[new_col_name] = df[col_a] - df[col_b]
                    elif op == "*":
                        st.session_state.cleaned_df[new_col_name] = df[col_a] * df[col_b]
                    elif op == "/":
                        st.session_state.cleaned_df[new_col_name] = df[col_a] / df[col_b].replace(0, np.nan)
                    
                    msg = f"Created derived column '{new_col_name}' ({col_a} {op} {col_b})"
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()

        elif f_type == "Date Part Extraction":
            # Find date columns
            date_candidates = []
            for c in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[c]) or "date" in c.lower() or "time" in c.lower():
                    date_candidates.append(c)
            
            if date_candidates:
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    target_date_col = st.selectbox("Date Column", date_candidates)
                with c_d2:
                    date_parts = st.multiselect("Extract Components", ["Year", "Month", "Quarter", "Day of Week"], default=["Year", "Month"])
                
                if st.button("Extract Date Parts", type="primary"):
                    date_series = pd.to_datetime(df[target_date_col], errors='coerce')
                    if "Year" in date_parts:
                        st.session_state.cleaned_df[f"{target_date_col}_Year"] = date_series.dt.year
                    if "Month" in date_parts:
                        st.session_state.cleaned_df[f"{target_date_col}_Month"] = date_series.dt.month_name()
                    if "Quarter" in date_parts:
                        st.session_state.cleaned_df[f"{target_date_col}_Quarter"] = date_series.dt.quarter
                    if "Day of Week" in date_parts:
                        st.session_state.cleaned_df[f"{target_date_col}_DayOfWeek"] = date_series.dt.day_name()
                    
                    msg = f"Extracted {date_parts} from '{target_date_col}'"
                    st.session_state.audit_log.append(msg)
                    st.success(msg)
                    st.rerun()
            else:
                st.info("No datetime candidate columns found. Cast a column to datetime first under 'Type Casting'.")

        elif f_type == "Drop Columns":
            cols_to_drop = st.multiselect("Select Columns to Remove", df.columns.tolist())
            if st.button("Drop Selected Columns", type="primary") and cols_to_drop:
                st.session_state.cleaned_df = df.drop(columns=cols_to_drop).copy()
                msg = f"Dropped columns: {cols_to_drop}"
                st.session_state.audit_log.append(msg)
                st.success(msg)
                st.rerun()

        elif f_type == "Rename Column":
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                old_name = st.selectbox("Existing Column", df.columns.tolist())
            with c_r2:
                new_name = st.text_input("New Name", value=old_name)
            
            if st.button("Rename Column", type="primary") and new_name and new_name != old_name:
                st.session_state.cleaned_df = df.rename(columns={old_name: new_name}).copy()
                msg = f"Renamed column '{old_name}' to '{new_name}'"
                st.session_state.audit_log.append(msg)
                st.success(msg)
                st.rerun()

    # 7. AUDIT LOG
    with clean_tabs[6]:
        st.markdown("##### Transformation Audit Trail")
        for i, log_entry in enumerate(st.session_state.audit_log, 1):
            st.markdown(f"**{i:02d}.** {log_entry}")


# ==============================================================================
# TAB 3: KEY METRICS & EXPLORATORY DATA ANALYSIS (EDA)
# ==============================================================================
with tab_metrics:
    st.subheader("Key Metrics & Statistical Distribution")

    eda_mode = st.radio(
        "EDA Perspective",
        ["Numerical Summary", "Categorical Summary", "Correlation Matrix", "Group-by Pivot"],
        horizontal=True
    )

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if eda_mode == "Numerical Summary":
        if not num_cols:
            st.info("No numerical columns found in the active dataset.")
        else:
            desc = df[num_cols].describe().T
            desc["skew"] = df[num_cols].skew()
            desc["kurtosis"] = df[num_cols].kurtosis()
            desc["IQR"] = desc["75%"] - desc["25%"]
            desc = desc.round(2)
            st.dataframe(desc, use_container_width=True)

            st.markdown("##### Distribution Visualizer")
            c_d_col, c_d_type = st.columns([2, 1])
            with c_d_col:
                selected_num = st.selectbox("Inspect Metric", num_cols, key="eda_metric_select")
            with c_d_type:
                chart_style = st.selectbox("Chart Style", ["Histogram + KDE", "Box Plot", "Violin Plot"])

            if chart_style == "Histogram + KDE":
                fig_dist = px.histogram(
                    df,
                    x=selected_num,
                    marginal="box",
                    nbins=30,
                    title=f"Distribution of {selected_num}",
                    color_discrete_sequence=["#2563eb"]
                )
            elif chart_style == "Box Plot":
                fig_dist = px.box(
                    df,
                    y=selected_num,
                    points="all",
                    title=f"Box Plot for {selected_num}",
                    color_discrete_sequence=["#0891b2"]
                )
            else:
                fig_dist = px.violin(
                    df,
                    y=selected_num,
                    box=True,
                    points="all",
                    title=f"Violin Plot for {selected_num}",
                    color_discrete_sequence=["#8b5cf6"]
                )
            fig_dist.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=380)
            st.plotly_chart(fig_dist, use_container_width=True)

    elif eda_mode == "Categorical Summary":
        if not cat_cols:
            st.info("No categorical columns available.")
        else:
            cat_summary = []
            for col in cat_cols:
                series = df[col].dropna()
                vc = series.value_counts()
                top_val = vc.index[0] if not vc.empty else "N/A"
                top_freq = int(vc.iloc[0]) if not vc.empty else 0
                cat_summary.append({
                    "Feature": col,
                    "Total Non-Null": int(series.count()),
                    "Unique Categories": int(series.nunique()),
                    "Top Category (Mode)": str(top_val),
                    "Top Category Count": top_freq,
                    "Top Category Share (%)": round(top_freq / len(series) * 100, 2) if len(series) > 0 else 0
                })
            st.dataframe(pd.DataFrame(cat_summary), use_container_width=True)

            st.markdown("##### Frequency Distribution")
            selected_cat = st.selectbox("Select Categorical Feature", cat_cols, key="eda_cat_select")
            top_n = st.slider("Top Categories to Display", min_value=3, max_value=25, value=10)
            
            top_vc = df[selected_cat].value_counts().head(top_n).reset_index()
            top_vc.columns = [selected_cat, "Frequency"]
            fig_cat = px.bar(
                top_vc,
                x=selected_cat,
                y="Frequency",
                text="Frequency",
                title=f"Top {top_n} Values in '{selected_cat}'",
                color="Frequency",
                color_continuous_scale="Blues"
            )
            fig_cat.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=380)
            st.plotly_chart(fig_cat, use_container_width=True)

    elif eda_mode == "Correlation Matrix":
        if len(num_cols) < 2:
            st.info("Need at least 2 numerical columns to calculate correlations.")
        else:
            corr_method = st.selectbox("Correlation Method", ["pearson", "spearman"])
            corr_matrix = df[num_cols].corr(method=corr_method).round(2)
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title=f"{corr_method.capitalize()} Correlation Heatmap"
            )
            fig_corr.update_layout(height=450, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_corr, use_container_width=True)

            # Top correlated pairs
            st.markdown("##### Strongest Correlated Pairs")
            unstacked = corr_matrix.unstack().reset_index()
            unstacked.columns = ['Feature 1', 'Feature 2', 'Correlation']
            unstacked = unstacked[unstacked['Feature 1'] != unstacked['Feature 2']]
            # Remove symmetry
            unstacked['abs_corr'] = unstacked['Correlation'].abs()
            unstacked = unstacked.sort_values(by='abs_corr', ascending=False).drop_duplicates(subset=['abs_corr'])
            st.dataframe(unstacked[['Feature 1', 'Feature 2', 'Correlation']].head(10), use_container_width=True)

    elif eda_mode == "Group-by Pivot":
        if not cat_cols or not num_cols:
            st.info("Requires at least one categorical and one numeric feature.")
        else:
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1:
                grp_col = st.selectbox("Group By (Primary)", cat_cols)
            with c_p2:
                val_col = st.selectbox("Value Metric", num_cols)
            with c_p3:
                agg_func = st.selectbox("Aggregation", ["mean", "sum", "median", "count", "min", "max", "std"])

            grouped = df.groupby(grp_col)[val_col].agg(agg_func).reset_index()
            grouped = grouped.sort_values(by=val_col, ascending=False).round(2)
            
            c_tbl, c_plt = st.columns([1, 2])
            with c_tbl:
                st.dataframe(grouped, use_container_width=True)
            with c_plt:
                fig_grp = px.bar(
                    grouped,
                    x=grp_col,
                    y=val_col,
                    text=val_col,
                    title=f"{agg_func.capitalize()} of {val_col} by {grp_col}",
                    color=val_col,
                    color_continuous_scale="Teal"
                )
                fig_grp.update_layout(height=360, margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(fig_grp, use_container_width=True)


# ==============================================================================
# TAB 4: INTERACTIVE FILTERABLE CHART STUDIO
# ==============================================================================
with tab_charts:
    st.subheader("Interactive Filterable Chart Studio")
    st.write("Apply real-time multi-dimensional filters and configure rich Plotly charts.")

    # 1. FILTER CONTROLS ACCORDION
    with st.expander("🔍 Interactive Data Filters (Filter before plotting)", expanded=True):
        f_cols = st.columns(3)
        filtered_df = df.copy()

        # Filter by Categoricals
        with f_cols[0]:
            st.markdown("**Categorical Filters**")
            top_cats_for_filter = [c for c in cat_cols if df[c].nunique() <= 30][:3]
            for cat_f in top_cats_for_filter:
                options = sorted(df[cat_f].dropna().unique().tolist())
                selected_vals = st.multiselect(f"Filter {cat_f}", options, default=options)
                if selected_vals:
                    filtered_df = filtered_df[filtered_df[cat_f].isin(selected_vals)]

        # Filter by Numerics
        with f_cols[1]:
            st.markdown("**Numerical Range Filters**")
            top_nums_for_filter = num_cols[:2]
            for num_f in top_nums_for_filter:
                col_min = float(df[num_f].min())
                col_max = float(df[num_f].max())
                if col_min < col_max:
                    selected_range = st.slider(
                        f"Range for {num_f}",
                        min_value=col_min,
                        max_value=col_max,
                        value=(col_min, col_max)
                    )
                    filtered_df = filtered_df[
                        (filtered_df[num_f] >= selected_range[0]) &
                        (filtered_df[num_f] <= selected_range[1])
                    ]

        # Filter by Dates
        with f_cols[2]:
            st.markdown("**Date Filter**")
            date_col_match = None
            for c in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[c]) or "date" in c.lower():
                    date_col_match = c
                    break
            
            if date_col_match:
                dt_series = pd.to_datetime(df[date_col_match], errors='coerce').dropna()
                if not dt_series.empty:
                    min_d = dt_series.min().date()
                    max_d = dt_series.max().date()
                    if min_d < max_d:
                        date_range = st.date_input(f"Date Span ({date_col_match})", [min_d, max_d])
                        if len(date_range) == 2:
                            dt_conv = pd.to_datetime(filtered_df[date_col_match], errors='coerce')
                            filtered_df = filtered_df[
                                (dt_conv.dt.date >= date_range[0]) & 
                                (dt_conv.dt.date <= date_range[1])
                            ]
            else:
                st.caption("No date column detected for range filtering.")

        st.caption(f"Filtered Records: **{len(filtered_df):,}** / {len(df):,} ({len(filtered_df)/len(df)*100:.1f}%)")

    # 2. CHART BUILDER INTERFACE
    st.markdown("#### Chart Builder")
    c_b1, c_b2, c_b3 = st.columns([2, 2, 2])
    with c_b1:
        chart_family = st.selectbox(
            "Chart Type",
            [
                "Scatter Plot",
                "Line / Time Series",
                "Bar Chart",
                "Histogram / Density",
                "Box Plot",
                "Pie / Donut",
                "Treemap"
            ]
        )
    with c_b2:
        color_palette = st.selectbox(
            "Color Theme",
            ["Plotly", "Viridis", "Plasma", "Tealgrn", "Sunset", "Blues", "Purples"]
        )
    with c_b3:
        chart_title = st.text_input("Chart Title", value=f"{chart_family} Analysis")

    # Dynamic inputs per chart type
    all_col_options = filtered_df.columns.tolist()
    fig = None

    if chart_family == "Scatter Plot":
        cs1, cs2, cs3, cs4 = st.columns(4)
        with cs1:
            x_axis = st.selectbox("X-Axis (Numeric)", num_cols, index=0 if len(num_cols) > 0 else 0)
        with cs2:
            y_axis = st.selectbox("Y-Axis (Numeric)", num_cols, index=1 if len(num_cols) > 1 else 0)
        with cs3:
            color_dim = st.selectbox("Color By (Optional)", ["None"] + all_col_options)
        with cs4:
            size_dim = st.selectbox("Size By (Numeric Optional)", ["None"] + num_cols)
        
        trendline = st.checkbox("Add OLS Trendline", value=False)
        
        color_arg = color_dim if color_dim != "None" else None
        size_arg = size_dim if size_dim != "None" else None
        
        if not filtered_df.empty and x_axis and y_axis:
            fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis,
                color=color_arg,
                size=size_arg,
                trendline="ols" if trendline else None,
                color_continuous_scale=color_palette if color_arg in num_cols else None,
                color_discrete_sequence=px.colors.qualitative.Plotly if color_arg in cat_cols else None,
                title=chart_title
            )

    elif chart_family == "Line / Time Series":
        cl1, cl2, cl3 = st.columns(3)
        with cl1:
            x_line = st.selectbox("X-Axis (Date or Sequence)", all_col_options)
        with cl2:
            y_line = st.selectbox("Y-Axis (Numeric)", num_cols)
        with cl3:
            group_line = st.selectbox("Group / Color By", ["None"] + cat_cols)

        group_arg = group_line if group_line != "None" else None
        if not filtered_df.empty and x_line and y_line:
            # Sort by x
            plot_data = filtered_df.sort_values(by=x_line)
            fig = px.line(
                plot_data,
                x=x_line,
                y=y_line,
                color=group_arg,
                markers=True,
                title=chart_title
            )

    elif chart_family == "Bar Chart":
        cb1, cb2, cb3, cb4 = st.columns(4)
        with cb1:
            x_bar = st.selectbox("X-Axis (Category or Feature)", all_col_options)
        with cb2:
            y_bar = st.selectbox("Y-Axis (Numeric)", num_cols)
        with cb3:
            color_bar = st.selectbox("Color By", ["None"] + cat_cols)
        with cb4:
            bar_mode = st.selectbox("Bar Mode", ["group", "stack", "relative"])

        color_arg = color_bar if color_bar != "None" else None
        if not filtered_df.empty and x_bar and y_bar:
            fig = px.bar(
                filtered_df,
                x=x_bar,
                y=y_bar,
                color=color_arg,
                barmode=bar_mode,
                title=chart_title
            )

    elif chart_family == "Histogram / Density":
        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            x_hist = st.selectbox("Feature to Bin", num_cols)
        with ch2:
            bins = st.slider("Number of Bins", 5, 80, 25)
        with ch3:
            marginal = st.selectbox("Marginal View", ["none", "box", "violin", "rug"])

        if not filtered_df.empty and x_hist:
            fig = px.histogram(
                filtered_df,
                x=x_hist,
                nbins=bins,
                marginal=None if marginal == "none" else marginal,
                title=chart_title,
                color_discrete_sequence=["#2563eb"]
            )

    elif chart_family == "Box Plot":
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            y_box = st.selectbox("Measurement Metric (Numeric)", num_cols)
        with cx2:
            x_box = st.selectbox("Group By Category (Optional)", ["None"] + cat_cols)
        with cx3:
            points_opt = st.selectbox("Show Points", ["outliers", "all", "none"])

        x_arg = x_box if x_box != "None" else None
        if not filtered_df.empty and y_box:
            fig = px.box(
                filtered_df,
                x=x_arg,
                y=y_box,
                points=False if points_opt == "none" else points_opt,
                title=chart_title,
                color=x_arg
            )

    elif chart_family == "Pie / Donut":
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            names_col = st.selectbox("Slice Categories", cat_cols)
        with cp2:
            values_col = st.selectbox("Values (Numeric)", num_cols)
        with cp3:
            donut_hole = st.slider("Donut Hole Size", 0.0, 0.7, 0.4, 0.1)

        if not filtered_df.empty and names_col and values_col:
            # Aggregate to avoid overcrowded pies
            pie_agg = filtered_df.groupby(names_col)[values_col].sum().reset_index()
            fig = px.pie(
                pie_agg,
                names=names_col,
                values=values_col,
                hole=donut_hole,
                title=chart_title
            )

    elif chart_family == "Treemap":
        ct1, ct2 = st.columns(2)
        with ct1:
            path_cols = st.multiselect("Hierarchy Path (1 to 3 categories)", cat_cols, default=cat_cols[:2])
        with ct2:
            val_tree = st.selectbox("Size Value (Numeric)", num_cols)

        if not filtered_df.empty and path_cols and val_tree:
            fig = px.treemap(
                filtered_df,
                path=path_cols,
                values=val_tree,
                title=chart_title
            )

    # Render Chart
    if fig is not None:
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=30),
            height=480
        )
        st.plotly_chart(fig, use_container_width=True)

        # Export chart as interactive HTML
        buffer = io.StringIO()
        fig.write_html(buffer, include_plotlyjs='cdn')
        html_bytes = buffer.getvalue().encode('utf-8')
        st.download_button(
            label="⬇ Download Chart as Standalone HTML",
            data=html_bytes,
            file_name=f"{chart_title.replace(' ', '_').lower()}.html",
            mime="text/html"
        )
    else:
        st.info("Configure your chart parameters above to render.")


# ==============================================================================
# TAB 5: EXPORTABLE REPORTS
# ==============================================================================
with tab_export:
    st.subheader("Exportable Reports & Data Delivery")
    st.write("Generate clean data assets and standalone executive reports ready for stakeholder distribution.")

    c_exp1, c_exp2 = st.columns(2)

    # Cleaned Datasets
    with c_exp1:
        st.markdown("##### 📁 Cleaned Data Assets")
        st.caption("Download the processed dataset reflecting all cleaning, transformations, and filters.")

        # CSV Download
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇ Download Cleaned Dataset (CSV)",
            data=csv_data,
            file_name=f"cleaned_{st.session_state.dataset_name.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Excel Download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='CleanedData')
            # Summary statistics sheet
            if num_cols:
                df[num_cols].describe().to_excel(writer, sheet_name='SummaryStats')
        excel_data = excel_buffer.getvalue()

        st.download_button(
            label="⬇ Download Cleaned Dataset (Excel .xlsx)",
            data=excel_data,
            file_name=f"cleaned_{st.session_state.dataset_name.replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Executive HTML Report
    with c_exp2:
        st.markdown("##### 📑 Executive HTML Data Report")
        st.caption("Self-contained styled HTML dossier containing metrics, missingness audit, descriptive statistics, and audit trail.")

        # HTML Report Generation
        def generate_html_report(data: pd.DataFrame, title: str, audit_logs: list) -> str:
            now_str = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
            n_rows = len(data)
            n_cols = len(data.columns)
            n_nulls = int(data.isnull().sum().sum())
            n_dups = int(data.duplicated().sum())

            num_sub = data.select_dtypes(include=[np.number])
            stats_html = num_sub.describe().round(2).to_html(classes="report-table") if not num_sub.empty else "<p>No numeric features.</p>"
            
            audit_html = "".join([f"<li>{item}</li>" for item in audit_logs])

            html_template = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{title} | Executive Analytics Dossier</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        color: #0f172a;
                        background-color: #f8fafc;
                        margin: 0;
                        padding: 40px 20px;
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        background: #ffffff;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                    }}
                    .header {{
                        border-bottom: 2px solid #e2e8f0;
                        padding-bottom: 24px;
                        margin-bottom: 30px;
                    }}
                    .header h1 {{
                        margin: 0 0 8px 0;
                        color: #1e293b;
                        font-size: 28px;
                    }}
                    .header p {{
                        margin: 0;
                        color: #64748b;
                        font-size: 14px;
                    }}
                    .kpi-grid {{
                        display: grid;
                        grid-template-columns: repeat(4, 1fr);
                        gap: 16px;
                        margin-bottom: 36px;
                    }}
                    .kpi-card {{
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        padding: 18px;
                        border-radius: 8px;
                    }}
                    .kpi-label {{
                        font-size: 12px;
                        font-weight: 600;
                        text-transform: uppercase;
                        color: #64748b;
                        letter-spacing: 0.05em;
                    }}
                    .kpi-val {{
                        font-size: 26px;
                        font-weight: 700;
                        color: #0f172a;
                        margin-top: 6px;
                    }}
                    h2 {{
                        color: #1e293b;
                        font-size: 18px;
                        margin-top: 32px;
                        margin-bottom: 16px;
                    }}
                    .report-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 13px;
                        margin-bottom: 24px;
                    }}
                    .report-table th, .report-table td {{
                        padding: 10px 14px;
                        border: 1px solid #e2e8f0;
                        text-align: left;
                    }}
                    .report-table th {{
                        background: #f1f5f9;
                        font-weight: 600;
                        color: #334155;
                    }}
                    .audit-list {{
                        background: #f8fafc;
                        border-left: 4px solid #2563eb;
                        padding: 14px 24px;
                        border-radius: 4px;
                    }}
                    .footer {{
                        margin-top: 48px;
                        padding-top: 20px;
                        border-top: 1px solid #e2e8f0;
                        color: #94a3b8;
                        font-size: 12px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{title}</h1>
                        <p>Generated on {now_str} via D-A-D (Data Analytics Dashboard Engine)</p>
                    </div>

                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-label">Records</div>
                            <div class="kpi-val">{n_rows:,}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">Attributes</div>
                            <div class="kpi-val">{n_cols}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">Missing Values</div>
                            <div class="kpi-val">{n_nulls:,}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">Duplicate Rows</div>
                            <div class="kpi-val">{n_dups:,}</div>
                        </div>
                    </div>

                    <h2>1. Descriptive Statistics</h2>
                    {stats_html}

                    <h2>2. Data Transformation & Cleaning Audit Log</h2>
                    <ul class="audit-list">
                        {audit_html}
                    </ul>

                    <div class="footer">
                        D-A-D · Automated Data Analytics & Cleaning Pipeline · Ready for Cloud Deployment
                    </div>
                </div>
            </body>
            </html>
            """
            return html_template

        report_html = generate_html_report(df, st.session_state.dataset_name, st.session_state.audit_log)
        st.download_button(
            label="⬇ Download Executive HTML Dossier",
            data=report_html.encode('utf-8'),
            file_name=f"executive_report_{st.session_state.dataset_name.replace(' ', '_').lower()}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("##### 📋 Summary Statistics (CSV)")
    if num_cols:
        stats_csv = df[num_cols].describe().to_csv().encode('utf-8')
        st.download_button(
            label="⬇ Download Summary Statistics (CSV)",
            data=stats_csv,
            file_name=f"summary_stats_{st.session_state.dataset_name.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )
