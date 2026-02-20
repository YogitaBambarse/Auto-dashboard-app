import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page setup
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
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    df = load_data(uploaded_file)
    st.success("✅ Dataset Loaded!")
    
    st.subheader("Dataset Preview")
    st.dataframe(df.head(1000))  # show max 1000 rows for fast browser render

    # Detect columns
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64','object']).columns.tolist()
    
    # Convert date columns automatically
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass

    # Sidebar Numeric Filters
    st.sidebar.subheader("Numeric Filters")
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        df = df[(df[col] >= st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val)))]

    # Sidebar Categorical Filters
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
            cols[0].metric("Max Speed", max_speed, delta="↑ High" if max_speed>120 else "↓ Low")
        if "Mileage" in numeric_cols:
            avg_mileage = round(df["Mileage"].mean(),2)
            cols[1].metric("Avg Mileage", avg_mileage, delta="↑ Good" if avg_mileage>20 else "↓ Low")
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
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page setup
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
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    df = load_data(uploaded_file)
    df.columns = df.columns.str.strip()  # remove extra spaces
    st.success("✅ Dataset Loaded!")
    
    st.subheader("Dataset Preview")
    st.dataframe(df.head(1000))  # max 1000 rows for performance

    # Detect columns
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64','object']).columns.tolist()
    
    # Convert date columns automatically
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')  # invalid → NaT
        except:
            pass

    # Sidebar Numeric Filters (safe)
    st.sidebar.subheader("Numeric Filters")
    for col in numeric_cols:
        # Force numeric and drop invalid
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=[col])
        if len(df[col]) == 0:
            continue  # skip empty column
        min_val, max_val = float(df[col].min()), float(df[col].max())
        range_val = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))
        df = df[(df[col] >= range_val[0]) & (df[col] <= range_val[1])]

    # Sidebar Categorical Filters
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
            cols[0].metric("Max Speed", max_speed, delta="↑ High" if max_speed>120 else "↓ Low")
        if "Mileage" in numeric_cols:
            avg_mileage = round(df["Mileage"].mean(),2)
            cols[1].metric("Avg Mileage", avg_mileage, delta="↑ Good" if avg_mileage>20 else "↓ Low")
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
                st.subheader("Correlation Heatmap (Top 10 numeric columns for performance)")
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
            for col in numeric_cols:
                sample_df = df.sample(n=min(len(df),2000))
                fig = px.line(sample_df, y=col, title=f"{col} Trend", template="plotly_white", markers=True)
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
    st.info("Upload a CSV or Excel file to generate the Fast & Professional Dashboard.")
