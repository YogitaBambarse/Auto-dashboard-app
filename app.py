import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Ultimate Auto Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Ultimate Professional Auto Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("Upload Dataset & Filters")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("✅ Dataset Loaded!")

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Sidebar Numeric Filters
    st.sidebar.subheader("Numeric Filters")
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        range_val = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))
        df = df[(df[col] >= range_val[0]) & (df[col] <= range_val[1])]

    # Sidebar Categorical Filters
    st.sidebar.subheader("Categorical Filters")
    for col in cat_cols:
        options = st.sidebar.multiselect(f"{col}", df[col].unique(), default=list(df[col].unique()))
        df = df[df[col].isin(options)]

    # Check if DataFrame is empty after filtering
    if df.empty:
        st.warning("⚠️ No data available after applying filters. Adjust filters or upload another CSV.")
    else:
        # KPIs
        st.markdown("## 📊 Key Metrics")
        cols = st.columns(4)
        if "Speed" in numeric_cols:
            cols[0].metric("Max Speed", df["Speed"].max())
        if "Mileage" in numeric_cols:
            cols[1].metric("Avg Mileage", round(df["Mileage"].mean(),2))
        cols[2].metric("Total Vehicles", len(df))
        cols[3].metric("Numeric Columns", len(numeric_cols))

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Summary", "Numeric Charts", "Categorical Analysis"])

        # Tab 1: Summary
        with tab1:
            st.subheader("Summary Statistics")
            st.write(df.describe(include='all'))
            st.subheader("Textual Insights")
            st.write(f"Total Rows: {len(df)}")
            if "Speed" in numeric_cols:
                st.write(f"Maximum Speed: {df['Speed'].max()}")
            if "Mileage" in numeric_cols:
                st.write(f"Average Mileage: {round(df['Mileage'].mean(),2)}")

        # Tab 2: Numeric Charts
        with tab2:
            if numeric_cols:
                st.subheader("Correlation Heatmap")
                corr = df[numeric_cols].corr()
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale='Viridis'
                ))
                st.plotly_chart(fig_corr, use_container_width=True)

                st.subheader("Scatter Plot")
                x_col = st.selectbox("X-axis", numeric_cols, index=0, key="xaxis")
                y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="yaxis")
                color_col = st.selectbox("Color Column", df.columns, index=0, key="colorcol")
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                                 hover_data=df.columns, color_continuous_scale="Viridis", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns to plot charts.")

        # Tab 3: Categorical Analysis
        with tab3:
            if cat_cols:
                st.subheader("Categorical Columns Distribution")
                for col in cat_cols:
                    fig = px.histogram(df, x=col, color=col,
                                       color_discrete_sequence=px.colors.qualitative.Pastel,
                                       template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categorical columns to plot.")

else:
    st.info("Upload a CSV or Excel file to generate the professional dashboard.")
    # Tab 2: Numeric Charts
    with tab2:
        if numeric_cols:
            st.subheader("Correlation Heatmap")
            corr = df[numeric_cols].corr()
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale='Viridis'
            ))
            st.plotly_chart(fig_corr, use_container_width=True)

            st.subheader("Scatter Plot")
            x_col = st.selectbox("X-axis", numeric_cols, index=0, key="xaxis")
            y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="yaxis")
            color_col = st.selectbox("Optional Color Column", df.columns, index=0, key="colorcol")
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, hover_data=df.columns,
                             color_continuous_scale="Viridis", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns for charts.")

    # Tab 3: Categorical Analysis
    with tab3:
        if cat_cols:
            st.subheader("Categorical Columns")
            for col in cat_cols:
                st.write(f"**{col} Distribution**")
                fig = px.histogram(df, x=col, color=col, color_discrete_sequence=px.colors.qualitative.Pastel,
                                   template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns for analysis.")

else:
    st.info("Upload a CSV or Excel file to generate the dashboard automatically.")
