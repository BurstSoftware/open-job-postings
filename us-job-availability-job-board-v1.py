import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Set page configuration
st.set_page_config(
    page_title="US Job Availability Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Raw Data & State Code Mapping for the Choropleth Map
data = {
    "State": [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", 
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
        "Wisconsin", "Wyoming"
    ],
    "Approximate Jobs Available": [
        79000, 21000, 140000, 42000, 600000, 122000, 70000, 18000, 400000, 180000, 25000, 
        40000, 235000, 100000, 65000, 80000, 60000, 50000, 25000, 122000, 162000, 188000, 
        105000, 41000, 95000, 25000, 40000, 52000, 25000, 168000, 40000, 303000, 175000, 
        20000, 242000, 50000, 75000, 256000, 20000, 100000, 16000, 125000, 500000, 75000, 
        17000, 175000, 125000, 32000, 100000, 15000
    ]
}

us_state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

# Load into DataFrame
df = pd.DataFrame(data)
df['State Code'] = df['State'].map(us_state_to_abbrev)

# 3. Sidebar UI Elements
st.sidebar.header("🎛️ Filter Options")

# Search/Select Specific States
selected_states = st.sidebar.multiselect(
    "Select States to Display:",
    options=df['State'].unique(),
    default=df['State'].unique()
)

# Slider for Job Range
min_jobs = int(df['Approximate Jobs Available'].min())
max_jobs = int(df['Approximate Jobs Available'].max())

job_range = st.sidebar.slider(
    "Filter by Minimum/Maximum Jobs:",
    min_value=min_jobs,
    max_value=max_jobs,
    value=(min_jobs, max_jobs)
)

# Filter the DataFrame based on inputs
filtered_df = df[
    (df['State'].isin(selected_states)) & 
    (df['Approximate Jobs Available'] >= job_range[0]) & 
    (df['Approximate Jobs Available'] <= job_range[1])
]

# 4. Main Panel UI Elements
st.title("💼 US Job Availability Market Overview")
st.markdown("Explore and filter approximate job availabilities across different US states.")

# Summary Metrics Row
if not filtered_df.empty:
    total_jobs = filtered_df['Approximate Jobs Available'].sum()
    highest_job_state = filtered_df.loc[filtered_df['Approximate Jobs Available'].idxmax()]
    lowest_job_state = filtered_df.loc[filtered_df['Approximate Jobs Available'].idxmin()]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs Found", f"{total_jobs:,}")
    col2.metric("Highest Market", f"{highest_job_state['State']}", f"{highest_job_state['Approximate Jobs Available']:,} jobs")
    col3.metric("Lowest Market", f"{lowest_job_state['State']}", f"{lowest_job_state['Approximate Jobs Available']:,} jobs")
else:
    st.warning("No data available based on current sidebar filters.")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Geographic Map", "📊 Charts & Breakdown", "📋 Raw Data"])

with tab1:
    st.subheader("Geographic Distribution of Jobs")
    if not filtered_df.empty:
        fig_map = px.choropleth(
            filtered_df,
            locations='State Code',
            locationmode="USA-states",
            color='Approximate Jobs Available',
            scope="usa",
            hover_name='State',
            color_continuous_scale="Viridis",
            labels={'Approximate Jobs Available': 'Jobs Available'}
        )
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Adjust your filters to see the map visualization.")

with tab2:
    st.subheader("Job Availability Rankings")
    if not filtered_df.empty:
        sort_order = st.radio("Sort Chart By:", ["Highest to Lowest", "Lowest to Highest"], horizontal=True)
        
        ascending_bool = True if sort_order == "Lowest to Highest" else False
        chart_df = filtered_df.sort_values(by='Approximate Jobs Available', ascending=ascending_bool)
        
        fig_bar = px.bar(
            chart_df,
            x='State',
            y='Approximate Jobs Available',
            color='Approximate Jobs Available',
            color_continuous_scale="Blues",
            labels={'Approximate Jobs Available': 'Jobs Available'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Adjust your filters to see the bar chart.")

with tab3:
    st.subheader("Data Overview Table")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['State', 'Approximate Jobs Available']].sort_values(by='Approximate Jobs Available', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No data matches your criteria.")
