import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Job Board",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 Open Job Postings")
st.markdown("All jobs from the dataset displayed as detailed cards")

# Load data
@st.cache_data
def load_jobs_from_github():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        expected_cols = ["id", "title", "company", "location", "salary", "posted", 
                        "type", "match", "website", "phone", "description", 
                        "requirements", "benefits", "referrer"]
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
                
        df['match'] = pd.to_numeric(df['match'], errors='coerce').fillna(0).astype(int)
        df['posted'] = pd.to_datetime(df['posted'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame(columns=["title", "company"])

df = load_jobs_from_github()

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")
search_term = st.sidebar.text_input("Search jobs", placeholder="Title, company, keywords...")
min_match = st.sidebar.slider("Minimum Match Score (%)", 0, 100, 0)

# Apply filters
filtered_df = df.copy()
if search_term:
    mask = (
        filtered_df['title'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['company'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['description'].astype(str).str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

filtered_df = filtered_df[filtered_df['match'] >= min_match]
filtered_df = filtered_df.sort_values(by='match', ascending=False)

st.sidebar.caption(f"Showing {len(filtered_df)} of {len(df)} jobs")

# Display Job Cards
st.header(f"Featured Jobs ({len(filtered_df)})")

if filtered_df.empty:
    st.info("No jobs match your current filters. Try lowering the match score or clearing the search.")
else:
    # 2 columns layout
    cols = st.columns(2)
    
    for idx, job in filtered_df.iterrows():
        col_idx = idx % 2
        with cols[col_idx]:
            with st.container(border=True):
                # Header
                st.subheader(job['title'])
                st.markdown(f"**{job['company']}**  •  {job.get('location', 'N/A')}")

                # Quick metrics
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Match", f"{int(job['match'])}%")
                with c2:
                    salary = job.get('salary')
                    if pd.notna(salary) and str(salary).strip():
                        st.success(f"💰 {salary}")
                with c3:
                    st.caption(job.get('type', 'N/A'))

                # Description
                st.markdown("**Description**")
                st.write(job.get('description', 'No description available.'))

                # Full details
                with st.expander("📋 All Job Details", expanded=False):
                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                        st.write(f"**ID:** {job.get('id', 'N/A')}")
                        posted = job['posted']
                        st.write(f"**Posted:** {posted.date() if pd.notna(posted) else 'N/A'}")
                        st.write(f"**Phone:** {job.get('phone', 'N/A')}")
                        st.write(f"**Referrer:** {job.get('referrer', 'N/A')}")
                    
                    with dcol2:
                        st.write("**Requirements**")
                        st.write(job.get('requirements', 'N/A'))
                        st.write("**Benefits**")
                        st.write(job.get('benefits', 'N/A'))

                # Action buttons
                b1, b2 = st.columns(2)
                with b1:
                    website = job.get('website')
                    if pd.notna(website) and str(website).strip():
                        st.link_button("🌐 Apply Now", website, use_container_width=True)
                    else:
                        st.button("Apply Now", disabled=True, use_container_width=True)
                with b2:
                    st.button("⭐ Save Job", key=f"save_{idx}", use_container_width=True)

st.divider()
st.caption("Data from: https://github.com/BurstSoftware/open-job-postings")
