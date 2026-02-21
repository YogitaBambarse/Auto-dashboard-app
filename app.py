import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ultimate Professional Dashboard", layout="wide")

st.title("🚀 Ultimate Professional & Safe Dashboard")
st.markdown("---")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.sidebar.header("Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:

    @st.cache_data
    def load_data(file):
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        df.columns = df.columns.str.strip()
        return df

    df = load_data(uploaded_file)

    # Keep original safe
    original_df = df.copy()

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(1000))

    # --------------------------------------------------
    # SMART DATE DETECTION (Safe)
    # --------------------------------------------------
    date_cols = []

    for col in df.columns:
        if df[col].dtype == "object":
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().sum() > 0.6 * len(df):
                df[col] = converted
                date_cols.append(col)

    # Detect types AFTER date conversion
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # --------------------------------------------------
    # FILTER SECTION
    # --------------------------------------------------
    st.sidebar.header("Filters")

    filtered_df = df.copy()

    # ---------------- Numeric Filters ----------------
    st.sidebar.subheader("Numeric Filters")

    for col in numeric_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")

        if filtered_df[col].dropna().empty:
            continue

        min_val = float(filtered_df[col].min())
        max_val = float(filtered_df[col].max())

        range_val = st.sidebar.slider(
            f"{col} Range",
            min_val,
            max_val,
            (min_val, max_val)
        )

        filtered_df = filtered_df[
            filtered_df[col].between(range_val[0], range_val[1])
        ]

    # ---------------- Categorical Filters ----------------
    st.sidebar.subheader("Categorical Filters")

    for col in cat_cols:
        filtered_df[col] = filtered_df[col].fillna("Missing").astype(str)

        unique_vals = filtered_df[col].unique()

        if len(unique_vals) <= 100:
            selected_vals = st.sidebar.multiselect(
                f"{col}",
                options=unique_vals,
                default=unique_vals
            )

            filtered_df = filtered_df[
                filtered_df[col].isin(selected_vals)
            ]
        else:
            st.sidebar.warning(f"{col} skipped (too many unique values)")

    df = filtered_df

    # --------------------------------------------------
    # EMPTY DATA PROTECTION
    # --------------------------------------------------
    if df.empty:
        st.warning("⚠️ No data available after applying filters.")
        st.stop()

    # --------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------
    st.markdown("## 📊 Key Metrics")
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total Rows", len(df))
    k2.metric("Numeric Columns", len(numeric_cols))
    k3.metric("Categorical Columns", len(cat_cols))
    k4.metric("Total Columns", len(df.columns))

    # --------------------------------------------------
    # TABS
    # --------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Summary", "Numeric Charts", "Categorical Analysis", "Time-Series"]
    )

    # ---------------- Summary ----------------
    with tab1:
        st.subheader("📋 Summary Statistics")
        st.write(df.describe(include="all"))

    # ---------------- Numeric Charts ----------------
    with tab2:
        if len(numeric_cols) >= 2:

            st.subheader("Correlation Heatmap")
            corr = df[numeric_cols[:10]].corr()

            fig_corr = go.Figure(
                data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale="Viridis"
                )
            )
            st.plotly_chart(fig_corr, use_container_width=True)

            st.subheader("Scatter Plot")

            x_axis = st.selectbox("X-Axis", numeric_cols)
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=1)

            color_option = None
            if cat_cols:
                color_option = st.selectbox("Color By", cat_cols)

            plot_df = df.dropna(subset=[x_axis, y_axis])

            if not plot_df.empty:
                sample_df = plot_df.sample(
                    n=min(len(plot_df), 2000),
                    random_state=42
                )

                fig = px.scatter(
                    sample_df,
                    x=x_axis,
                    y=y_axis,
                    color=color_option,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Need at least 2 numeric columns for charts.")

    # ---------------- Categorical Analysis ----------------
    with tab3:
        if cat_cols:

            st.subheader("Categorical Distribution")

            for col in cat_cols:
                plot_df = df[col].value_counts().reset_index()
                plot_df.columns = [col, "Count"]

                fig = px.bar(
                    plot_df,
                    x=col,
                    y="Count",
                    color=col,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No categorical columns found.")

    # ---------------- Time Series ----------------
    with tab4:
        if date_cols and numeric_cols:

            date_col = st.selectbox("Select Date Column", date_cols)

            for num_col in numeric_cols:
                plot_df = df.dropna(subset=[date_col, num_col])

                if not plot_df.empty:
                    fig = px.line(
                        plot_df,
                        x=date_col,
                        y=num_col,
                        template="plotly_white",
                        markers=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No valid date columns detected.")

    # --------------------------------------------------
    # DOWNLOAD FILTERED DATA
    # --------------------------------------------------
    st.download_button(
        "📥 Download Filtered Data",
        df.to_csv(index=False).encode("utf-8"),
        "filtered_data.csv",
        "text/csv"
    )

else:
    st.info("Please upload a CSV or Excel file to start.")