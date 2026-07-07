import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Job Board",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 Open Job Postings")
st.markdown("Discover exciting job opportunities from the community dataset.")

# Load data function
@st.cache_data
def load_jobs_from_github():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        # Ensure all required columns exist
        expected_cols = ["id", "title", "company", "location", "salary", "posted", 
                        "type", "match", "website", "phone", "description", 
                        "requirements", "benefits", "referrer"]
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None  # or a default value
        
        # Clean up data
        df['match'] = pd.to_numeric(df['match'], errors='coerce').fillna(0).astype(int)
        df['posted'] = pd.to_datetime(df['posted'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Failed to load jobs: {e}")
        return pd.DataFrame()

# Load the data
df = load_jobs_from_github()

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Search
search_term = st.sidebar.text_input("Search jobs", placeholder="Job title, company, skills...")

# Location filter
locations = ["All"] + sorted(df['location'].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("Location", locations)

# Job type filter
types = ["All"] + sorted(df['type'].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Job Type", types)

# Match score filter
min_match = st.sidebar.slider("Minimum Match Score (%)", 0, 100, 70)

# Salary filter (if salary is parseable)
salary_filter = st.sidebar.checkbox("Filter by salary (where available)", value=False)

# Apply filters
filtered_df = df.copy()

if search_term:
    search_mask = (
        filtered_df['title'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['company'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['description'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['requirements'].astype(str).str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[search_mask]

if selected_location != "All":
    filtered_df = filtered_df[filtered_df['location'] == selected_location]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == selected_type]

filtered_df = filtered_df[filtered_df['match'] >= min_match]

if salary_filter:
    # Simple salary presence filter
    filtered_df = filtered_df[filtered_df['salary'].notna() & (filtered_df['salary'].astype(str).str.strip() != "")]

# Sort by match score descending
filtered_df = filtered_df.sort_values(by='match', ascending=False)

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered_df)} of {len(df)} jobs")

# Display jobs as beautiful cards
st.header(f"Featured Jobs ({len(filtered_df)})")

if filtered_df.empty:
    st.info("No jobs match your filters. Try broadening your search.")
else:
    # Create columns for better layout (3 cards per row)
    cols = st.columns(3)
    
    for idx, job in filtered_df.iterrows():
        col_idx = idx % 3
        with cols[col_idx]:
            with st.container(border=True):
                # Header
                st.subheader(job['title'])
                
                # Company and location
                st.markdown(f"**{job['company']}** • {job['location']}")
                
                # Salary and type
                col1, col2 = st.columns([2, 1])
                with col1:
                    if pd.notna(job['salary']) and str(job['salary']).strip():
                        st.success(f"💰 {job['salary']}")
                with col2:
                    st.caption(job['type'])
                
                # Match score
                match_score = int(job['match'])
                if match_score >= 90:
                    color = "🟢"
                elif match_score >= 75:
                    color = "🟡"
                else:
                    color = "🔴"
                st.markdown(f"{color} **Match: {match_score}%**")
                
                # Description (truncated)
                desc = str(job['description'])[:180] + "..." if len(str(job['description'])) > 180 else str(job['description'])
                st.write(desc)
                
                # Key details in expander
                with st.expander("Requirements & Benefits"):
                    if pd.notna(job['requirements']) and str(job['requirements']).strip():
                        st.markdown("**Requirements:**")
                        st.write(job['requirements'])
                    if pd.notna(job['benefits']) and str(job['benefits']).strip():
                        st.markdown("**Benefits:**")
                        st.write(job['benefits'])
                
                # Action buttons
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if pd.notna(job['website']) and str(job['website']).strip():
                        st.link_button("Apply Now", job['website'], use_container_width=True)
                    else:
                        st.button("Apply Now", disabled=True, use_container_width=True)
                
                with btn_col2:
                    st.button("Save", key=f"save_{idx}", use_container_width=True)
                
                # Footer info
                posted_date = job['posted']
                if pd.notna(posted_date):
                    days_ago = (datetime.now() - posted_date).days
                    st.caption(f"Posted {days_ago} days ago • ID: {job.get('id', 'N/A')}")

# Additional stats
st.divider()
col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("Total Jobs", len(df))
with col_stats2:
    st.metric("Avg Match Score", f"{df['match'].mean():.1f}%" if not df.empty else "N/A")
with col_stats3:
    st.metric("Unique Companies", df['company'].nunique())

st.caption("Data sourced from [BurstSoftware/open-job-postings](https://github.com/BurstSoftware/open-job-postings)")
