import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Ultimate Fast Dashboard", layout="wide")

st.title("🚀 Ultimate Professional & Fast Dashboard")
st.markdown("---")

# Sidebar: Upload & Filters
st.sidebar.header("Upload Dataset & Filters")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])

if uploaded_file:
    # Cache data loading
    @st.cache_data
    def load_data(file):
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        df.columns = df.columns.str.strip()
        return df

    df = load_data(uploaded_file)
    st.subheader("Dataset Preview")
    st.dataframe(df.head(1000))

    # Detect columns
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64','object']).columns.tolist()

    # Convert date columns safely
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except:
            pass

    # Safe Numeric Filters
    st.sidebar.subheader("Numeric Filters")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=[col])
        if len(df[col]) == 0:
            continue
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        range_val = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))
        df = df[df[col].between(range_val[0], range_val[1])]

    # Categorical Filters
    st.sidebar.subheader("Categorical Filters")
    for col in cat_cols:
        if df[col].dropna().empty:
            continue
        options = st.sidebar.multiselect(f"{col}", df[col].dropna().unique(), default=list(df[col].dropna().unique()))
        df = df[df[col].isin(options)]

    if df.empty:
        st.warning("⚠️ No data available after filters.")
    else:
        # KPIs
        st.markdown("## 📊 Key Metrics")
        cols = st.columns(4)
        if "Speed" in numeric_cols:
            cols[0].metric("Max Speed", df["Speed"].max())
        if "Mileage" in numeric_cols:
            cols[1].metric("Avg Mileage", round(df["Mileage"].mean(),2))
        cols[2].metric("Total Rows", len(df))
        cols[3].metric("Numeric Columns", len(numeric_cols))

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Numeric Charts", "Categorical Analysis", "Trends / Time-Series"])

        with tab1:
            st.subheader("Summary Statistics")
            st.write(df.describe(include='all'))

        with tab2:
            if numeric_cols:
                st.subheader("Correlation Heatmap (Top 10 numeric columns)")
                top_numeric = numeric_cols[:10]
                corr = df[top_numeric].corr()
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale='Viridis'
                ))
                st.plotly_chart(fig_corr, use_container_width=True)

                st.subheader("Scatter Plot (Sampled for large datasets)")
                x_col = st.selectbox("X-axis", numeric_cols, index=0, key="xaxis")
                y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="yaxis")
                color_col = st.selectbox("Color Column", df.columns, index=0, key="colorcol")
                sample_df = df.sample(n=min(len(df),2000))
                fig = px.scatter(sample_df, x=x_col, y=y_col, color=color_col,
                                 hover_data=df.columns, color_continuous_scale="Viridis",
                                 template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns to plot charts.")

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

        with tab4:
            st.subheader("Numeric Trends / Time-Series")
            for col in numeric_cols:
                sample_df = df.sample(n=min(len(df),2000))
                fig = px.line(sample_df, y=col, title=f"{col} Trend", template="plotly_white", markers=True)
                st.plotly_chart(fig, use_container_width=True)

            date_cols_filtered = [c for c in date_cols if pd.api.types.is_datetime64_any_dtype(df[c])]
            if date_cols_filtered:
                date_col = st.selectbox("Select Date Column", date_cols_filtered)
                for num_col in numeric_cols:
                    fig = px.line(df, x=date_col, y=num_col, color=cat_cols[0] if cat_cols else None,
                                  title=f"{num_col} over Time", template="plotly_white", markers=True)
                    st.plotly_chart(fig, use_container_width=True)

        # Download filtered CSV
        st.download_button("📥 Download Filtered CSV", df.to_csv(index=False).encode('utf-8'), "filtered.csv", "text/csv")

else:
    st.info("Upload CSV/Excel file to start dashboard")