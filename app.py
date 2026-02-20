import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Auto Dashboard", layout="wide")

st.title("🚀 Dynamic Auto Dashboard App")

# Sidebar
st.sidebar.header("Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    st.success("Dataset Loaded Successfully!")
    
    # Show dataframe
    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # Quick statistics
    st.subheader("Summary Statistics")
    st.write(df.describe(include='all'))

    # Select numeric columns for charts
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if numeric_cols:
        st.subheader("Numeric Columns Charts")

        # Correlation heatmap
        corr = df[numeric_cols].corr()
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='Viridis'
        ))
        st.plotly_chart(fig_corr, use_container_width=True)

        # Scatter plots (all numeric vs numeric)
        st.subheader("Scatter Plots")
        x_col = st.selectbox("X-axis", numeric_cols, index=0)
        y_col = st.selectbox("Y-axis", numeric_cols, index=1)
        color_col = st.selectbox("Optional Color Column", df.columns, index=0)
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, hover_data=df.columns)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns found for charting.")

    # Categorical columns
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        st.subheader("Categorical Columns Analysis")
        for col in cat_cols:
            st.write(f"**{col} Distribution**")
            fig = px.histogram(df, x=col, color=col)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Upload a CSV file to generate dashboard automatically.")

# Custom CSS/JS
st.markdown("""
<link rel="stylesheet" href="assets/style.css">
<script src="assets/script.js"></script>
""", unsafe_allow_html=True)
