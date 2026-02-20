import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Professional Auto Dashboard", layout="wide")

st.title("🚀 Professional Auto Dashboard")
st.markdown("---")

# Sidebar: Upload + Filters
st.sidebar.header("Upload Dataset & Filters")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])

if uploaded_file:
    # Read CSV
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("✅ Dataset Loaded Successfully!")
    
    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Sidebar Filters for numeric
    st.sidebar.subheader("Numeric Filters")
    filters = {}
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        selected_range = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))
        filters[col] = selected_range
        df = df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

    # Sidebar Filters for categorical
    if cat_cols:
        st.sidebar.subheader("Categorical Filters")
        for col in cat_cols:
            options = st.sidebar.multiselect(f"Select {col}", df[col].unique(), default=list(df[col].unique()))
            df = df[df[col].isin(options)]

    st.markdown("## 📊 Key Metrics")
    # KPIs
    col1, col2, col3 = st.columns(3)
    if "Speed" in numeric_cols:
        col1.metric("Max Speed", df["Speed"].max())
    if "Mileage" in numeric_cols:
        col2.metric("Avg Mileage", round(df["Mileage"].mean(),2))
    col3.metric("Total Rows", len(df))

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Summary", "Numeric Charts", "Categorical Analysis"])

    # Tab 1: Summary
    with tab1:
        st.subheader("Summary Statistics")
        st.write(df.describe(include='all'))

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
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, hover_data=df.columns, color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns for charts.")

    # Tab 3: Categorical Analysis
    with tab3:
        if cat_cols:
            st.subheader("Categorical Columns")
            for col in cat_cols:
                st.write(f"**{col} Distribution**")
                fig = px.histogram(df, x=col, color=col, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns for analysis.")

else:
    st.info("Upload a CSV or Excel file to generate the dashboard automatically.")
