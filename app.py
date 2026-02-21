import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Ultimate Attractive Dashboard", layout="wide")
st.title("🚀 Ultimate Professional & Attractive Dashboard")
st.markdown("---")

# Sidebar: Upload & Filters
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
    date_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()

    # Convert date columns automatically
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass

    # Sidebar Filters: Numeric
    st.sidebar.subheader("Numeric Filters")
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        df = df[(df[col] >= st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val)))]

    # Sidebar Filters: Categorical
    st.sidebar.subheader("Categorical Filters")
    for col in cat_cols:
        options = st.sidebar.multiselect(f"{col}", df[col].unique(), default=list(df[col].unique()))
        df = df[df[col].isin(options)]

    # Empty dataset handling
    if df.empty:
        st.warning("⚠️ No data available after applying filters. Adjust filters or upload another CSV.")
    else:
        # Top KPIs
        st.markdown("## 📊 Key Metrics")
        cols = st.columns(4)
        if "Speed" in numeric_cols:
            max_speed = df["Speed"].max()
            cols[0].metric("Max Speed", max_speed, delta="↑ High" if max_speed > 120 else "↓ Low")
        if "Mileage" in numeric_cols:
            avg_mileage = round(df["Mileage"].mean(),2)
            cols[1].metric("Avg Mileage", avg_mileage, delta="↑ Good" if avg_mileage > 20 else "↓ Low")
        cols[2].metric("Total Vehicles", len(df))
        cols[3].metric("Numeric Columns", len(numeric_cols))

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Numeric Charts", "Categorical Analysis", "Trends / Time-Series"])

        # Tab 1: Summary
        with tab1:
            st.subheader("Summary Statistics")
            st.write(df.describe(include='all'))
            st.subheader("Textual Insights")
            st.write(f"Total Rows: {len(df)}")
            if "Speed" in numeric_cols:
                st.write(f"Maximum Speed: {max_speed}")
            if "Mileage" in numeric_cols:
                st.write(f"Average Mileage: {avg_mileage}")

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
                                 hover_data=df.columns, color_continuous_scale="Viridis",
                                 template="plotly_white")
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

        # Tab 4: Trends / Time-Series
        with tab4:
            st.subheader("Numeric Trends / Time-Series")
            # Line chart trends for numeric columns
            for col in numeric_cols:
                fig = px.line(df, y=col, title=f"{col} Trend", template="plotly_white", markers=True)
                st.plotly_chart(fig, use_container_width=True)

            # Time-series if Date exists
            date_cols_filtered = [c for c in date_cols if pd.api.types.is_datetime64_any_dtype(df[c])]
            if date_cols_filtered:
                date_col = st.selectbox("Select Date Column", date_cols_filtered)
                for num_col in numeric_cols:
                    fig = px.line(df, x=date_col, y=num_col, color=cat_cols[0] if cat_cols else None,
                                  title=f"{num_col} over Time", template="plotly_white", markers=True)
                    st.plotly_chart(fig, use_container_width=True)

        # Download filtered CSV
        st.download_button(label="📥 Download Filtered CSV",
                           data=df.to_csv(index=False).encode('utf-8'),
                           file_name="filtered_data.csv", mime="text/csv")

else:
    st.info("Upload a CSV or Excel file to generate the Ultimate Professional Dashboard.")