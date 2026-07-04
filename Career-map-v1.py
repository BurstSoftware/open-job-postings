import pandas as pd
import streamlit as st
import io

# 1. Page Configuration
st.set_page_config(
    page_title="US Career Map Explorer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Raw Data Integration
raw_data = """State,City,Sample_Positions
Alabama,Huntsville,"Production Associate, Retail Sales Associate (e.g. Trader Joe’s), City jobs (Equipment Operator, Digital Forensic Analyst, Aquatic Instructor), Healthcare roles, Warehouse/Logistics"
Alaska,Anchorage,"Government/admin roles, Healthcare (nurses, techs), Retail/Hospitality, Construction/Trades, Logistics"
Arizona,Phoenix,"Warehouse Associate/Order Picker, Security Screener, Delivery Driver, IT Support/Help Desk, Healthcare roles"
Arkansas,Little Rock,"Healthcare, Manufacturing/Production, Government/Admin, Retail, Transportation"
California,Los Angeles,"Healthcare (e.g. Cedars-Sinai roles), Retail/Cashier/Stocker, Warehouse/Logistics, Entertainment-related, Professional services"
Colorado,Denver,"Tech/Software roles, Healthcare, Construction/Trades, Retail/Hospitality, Government"
Connecticut,Bridgeport/Hartford,"Healthcare, Finance/Admin, Manufacturing, Education"
Delaware,Wilmington,"Finance/Admin, Healthcare, Manufacturing, Government"
Florida,Jacksonville,"Healthcare, Logistics/Warehouse, Hospitality/Retail, Construction, Finance"
Georgia,Atlanta,"Corporate/Admin, Logistics, Healthcare, Tech, Entertainment-related"
Hawaii,Honolulu,"Hospitality/Tourism, Healthcare, Government, Retail, Construction"
Idaho,Boise,"Tech/Manufacturing, Healthcare, Agriculture-related, Government"
Illinois,Chicago,"Finance, Healthcare, Logistics/Warehouse, Manufacturing, Tech"
Indiana,Indianapolis,"Manufacturing, Healthcare, Logistics, Finance/Admin"
Iowa,Des Moines,"Agribusiness, Finance/Insurance, Manufacturing, Healthcare"
Kansas,Wichita,"Aerospace/Manufacturing, Healthcare, Agriculture-related"
Kentucky,Louisville,"Logistics/Warehouse, Manufacturing, Healthcare"
Louisiana,New Orleans,"Energy, Hospitality/Tourism, Healthcare, Logistics"
Maine,Portland,"Healthcare, Tourism/Hospitality, Manufacturing, Government"
Maryland,Baltimore/DC area,"Government/Contracting, Healthcare/Biotech, Tech, Education"
Massachusetts,Boston,"Biotech/Tech, Healthcare, Finance, Education/Research"
Michigan,Detroit area,"Manufacturing/Auto, Healthcare, Tech, Logistics"
Minnesota,Minneapolis–Saint Paul,"Healthcare, Finance, Manufacturing, Tech"
Mississippi,Jackson,"Healthcare, Manufacturing, Government"
Missouri,Kansas City/St. Louis,"Healthcare, Manufacturing, Finance, Logistics"
Montana,Billings,"Healthcare, Energy, Tourism/Hospitality, Government"
Nebraska,Omaha,"Finance/Insurance, Healthcare, Agribusiness, Manufacturing"
Nevada,Las Vegas,"Hospitality/Gaming, Healthcare, Construction, Logistics"
New Hampshire,Manchester/Nashua,"Healthcare, Manufacturing, Tech"
New Jersey, Newark/Jersey City,"Finance, Pharma/Biotech, Logistics, Healthcare"
New Mexico,Albuquerque,"Government/Research, Healthcare, Energy, Tourism"
New York,New York City,"Finance, Tech, Healthcare, Media/Entertainment"
North Carolina,Charlotte,"Finance, Healthcare, Tech, Manufacturing, Logistics"
North Dakota,Fargo,"Energy, Agribusiness, Healthcare, Manufacturing"
Ohio,Columbus,"Healthcare, Finance, Manufacturing, Logistics"
Oklahoma,Oklahoma City,"Energy, Aerospace, Healthcare, Manufacturing"
Oregon,Portland,"Tech, Manufacturing, Healthcare, Agriculture/Food Processing"
Pennsylvania,Philadelphia,"Healthcare/Pharma, Finance, Education, Manufacturing"
Rhode Island,Providence,"Healthcare, Manufacturing, Education, Tourism"
South Carolina,Charleston,"Tourism/Hospitality, Manufacturing, Healthcare, Logistics"
South Dakota,Sioux Falls,"Healthcare, Finance, Agribusiness, Manufacturing"
Tennessee,Nashville,"Healthcare, Entertainment/Music, Finance, Manufacturing, Tourism"
Texas,Houston,"Energy, Healthcare, Aerospace, Logistics, Manufacturing"
Utah,Salt Lake City,"Tech, Finance, Healthcare, Manufacturing"
Vermont,Burlington,"Healthcare, Education, Tourism, Manufacturing"
Virginia,Virginia Beach/DC area,"Government/Defense Contracting, Healthcare, Tech, Logistics"
Washington,Seattle,"Tech/Software, Aerospace, Healthcare, Manufacturing"
West Virginia,Charleston,"Healthcare, Energy, Manufacturing, Government"
Wisconsin,Milwaukee,"Manufacturing, Healthcare, Finance, Agribusiness"
Wyoming,Cheyenne,"Energy, Government, Tourism/Hospitality, Healthcare" """

@st.cache_data
def load_data():
    df = pd.read_csv(io.StringIO(raw_data.strip()))
    # Clean whitespace
    df['State'] = df['State'].str.strip()
    df['City'] = df['City'].str.strip()
    df['Sample_Positions'] = df['Sample_Positions'].str.strip()
    return df

df = load_data()

# 3. Application Header
st.title("💼 US Career Market & Positions Navigator")
st.markdown("""
Explore trending sample positions, core industries, and key employment sectors across 50 US states and major hub cities. Use the filters on the left to pin down specific opportunities.
""")
st.write("---")

# 4. Sidebar / Filters
st.sidebar.header("🔍 Filter Options")

# Search by Keyword
search_query = st.sidebar.text_input("Search Positions (e.g., 'Tech', 'Healthcare')", "")

# Filter by State
all_states = sorted(df['State'].unique())
selected_states = st.sidebar.multiselect("Select States", options=all_states, default=[])

# Filter logic
filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]

if search_query:
    filtered_df = filtered_df[filtered_df['Sample_Positions'].str.contains(search_query, case=False, na=False)]

# 5. Dashboard Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total States Listed", len(df['State'].unique()))
with col2:
    st.metric("Hub Cities Covered", len(df['City'].unique()))
with col3:
    st.metric("Matching Results", len(filtered_df))

st.write("---")

# 6. Main Content Tabs
tab1, tab2, tab3 = st.tabs(["📊 Interactive Data View", "🎲 Serendipity (Random Career Picker)", "📈 Market Overview"])

with tab1:
    st.subheader("Explore Available Position Data")
    if filtered_df.empty:
        st.warning("No data matches your current filters. Try loosening your keywords!")
    else:
        st.dataframe(
            filtered_df, 
            column_config={
                "State": st.column_config.TextColumn("US State"),
                "City": st.column_config.TextColumn("Hub City/Area"),
                "Sample_Positions": st.column_config.TextColumn("In-Demand Roles / Sectors")
            }, 
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("Where Should You Move Next?")
    st.caption("Click the button below to get inspired by a random city and its career opportunities.")
    
    if st.button("🎲 Generate Random Career Path", type="primary"):
        random_row = df.sample(n=1).iloc[0]
        
        st.balloons()
        st.success(f"### Destination Found: {random_row['City']}, {random_row['State']}")
        
        st.markdown("**Top Sample Positions & Core Sectors:**")
        positions_list = [p.strip() for p in random_row['Sample_Positions'].split(',')]
        for position in positions_list:
            st.markdown(f"- {position}")

with tab3:
    st.subheader("Quick Industry Breakdown")
    
    # Simple tag parsing for common sectors
    industries = ['Healthcare', 'Tech', 'Finance', 'Manufacturing', 'Logistics', 'Government', 'Tourism']
    counts = {ind: 0 for ind in industries}
    
    for _, row in df.iterrows():
        for ind in industries:
            if ind.lower() in row['Sample_Positions'].lower():
                counts[ind] += 1
                
    chart_df = pd.DataFrame(list(counts.items()), columns=['Industry/Sector', 'State Hub Count']).sort_values(by='State Hub Count', ascending=False)
    
    st.markdown("This chart counts how many times a key sector keyword shows up explicitly in the states' position listings:")
    st.bar_chart(chart_df, x='Industry/Sector', y='State Hub Count', color='#ff4b4b')
