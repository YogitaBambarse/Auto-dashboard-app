import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Universal Auto Dashboard", layout="wide")

st.title("🚀 Universal Auto Dataset Dashboard")
st.markdown("---")

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

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(500))

    # --------------------------------------------------
    # AUTO TYPE DETECTION (VERY IMPORTANT)
    # --------------------------------------------------

    numeric_cols = []
    date_cols = []
    cat_cols = []

    for col in df.columns:

        # Try numeric
        converted_num = pd.to_numeric(df[col], errors="coerce")
        if converted_num.notna().sum() > 0.7 * len(df):
            df[col] = converted_num
            numeric_cols.append(col)
            continue

        # Try date
        converted_date = pd.to_datetime(df[col], errors="coerce")
        if converted_date.notna().sum() > 0.7 * len(df):
            df[col] = converted_date
            date_cols.append(col)
            continue

        # Else categorical
        cat_cols.append(col)

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    st.sidebar.header("Filters")

    filtered_df = df.copy()

    # Numeric filters
    if numeric_cols:
        st.sidebar.subheader("Numeric Filters")
        for col in numeric_cols:
            min_val = float(filtered_df[col].min())
            max_val = float(filtered_df[col].max())

            range_val = st.sidebar.slider(
                f"{col}",
                min_val,
                max_val,
                (min_val, max_val)
            )

            filtered_df = filtered_df[
                filtered_df[col].between(range_val[0], range_val[1])
            ]

    # Categorical filters
    if cat_cols:
        st.sidebar.subheader("Categorical Filters")
        for col in cat_cols:
            filtered_df[col] = filtered_df[col].fillna("Missing").astype(str)
            unique_vals = filtered_df[col].unique()

            if len(unique_vals) <= 100:
                selected = st.sidebar.multiselect(
                    col,
                    unique_vals,
                    default=unique_vals
                )
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

    df = filtered_df

    if df.empty:
        st.warning("No data after filters.")
        st.stop()

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    st.markdown("## 📊 Key Metrics")
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Rows", len(df))
    k2.metric("Numeric Columns", len(numeric_cols))
    k3.metric("Categorical Columns", len(cat_cols))
    k4.metric("Date Columns", len(date_cols))

    # --------------------------------------------------
    # TABS
    # --------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Summary", "Numeric Charts", "Categorical Charts", "Time Series"]
    )

    # Summary
    with tab1:
        st.write(df.describe(include="all"))

    # Numeric Charts
    with tab2:
        if len(numeric_cols) >= 2:

            st.subheader("Correlation Heatmap")
            corr = df[numeric_cols[:10]].corr()

            fig = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale="Viridis"
            ))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Scatter Plot")

            x = st.selectbox("X Axis", numeric_cols)
            y = st.selectbox("Y Axis", numeric_cols, index=1)

            fig2 = px.scatter(
                df,
                x=x,
                y=y,
                template="plotly_white"
            )
            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("Need at least 2 numeric columns.")

    # Categorical Charts
    with tab3:
        if cat_cols:
            for col in cat_cols:
                plot_df = df[col].value_counts().reset_index()
                plot_df.columns = [col, "Count"]

                fig = px.bar(
                    plot_df,
                    x=col,
                    y="Count",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No categorical columns found.")

    # Time Series
    with tab4:
        if date_cols and numeric_cols:
            date_col = st.selectbox("Select Date", date_cols)
            num_col = st.selectbox("Select Numeric", numeric_cols)

            fig = px.line(
                df,
                x=date_col,
                y=num_col,
                template="plotly_white",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No valid date & numeric combination found.")

else:
    st.info("Upload any dataset to generate dashboard.")