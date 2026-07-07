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
st.markdown("All jobs from the dataset displayed as cards")

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
        return pd.DataFrame()

df = load_jobs_from_github()

if df.empty:
    st.stop()

# Sidebar filters (kept for usability)
st.sidebar.header("🔍 Filters")
search_term = st.sidebar.text_input("Search", placeholder="Title, company, description...")
min_match = st.sidebar.slider("Minimum Match Score", 0, 100, 0)

# Apply simple filters
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

st.sidebar.caption(f"Showing {len(filtered_df)} jobs")

# Display as Job Cards
st.header(f"Job Cards ({len(filtered_df)})")

if filtered_df.empty:
    st.warning("No jobs found.")
else:
    cols = st.columns(2)  # 2 cards per row for more space

    for idx, job in filtered_df.iterrows():
        with cols[idx % 2]:
            with st.container(border=True):
                # Main Header
                st.subheader(f"{job['title']}")
                st.markdown(f"**{job['company']}** • {job.get('location', 'N/A')}")

                # Key info row
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Match", f"{int(job['match'])}%")
                with c2:
                    if pd.notna(job['salary']) and str(job['salary']).strip():
                        st.success(f"💰 {job['salary']}")
                with c3:
                    st.caption(job.get('type', 'N/A'))

                # Full Description
                st.markdown("**Description**")
                st.write(job.get('description', 'No description provided.'))

                # All other fields in expanders
                with st.expander("📋 Full Job Details", expanded=False):
                    detail_cols = st.columns(2)
                    with detail_cols[0]:
                        st.markdown(f"**ID:** {job.get('id', 'N/A')}")
                        st.markdown(f"**Posted:** {job['posted'].date() if pd.notna(job['posted']) else 'N/A'}")
                        st.markdown(f"**Phone:** {job.get('phone', 'N/A')}")
                        st.markdown(f"**Referrer:** {job.get('referrer', 'N/A')}")
                    
                    with detail_cols[1]:
                        st.markdown(f"**Requirements**")
                        st.write(job.get('requirements', 'N/A'))
                        st.markdown(f"**Benefits**")
                        st.write(job.get('benefits', 'N/A'))

                # Action buttons
                btn1, btn2 = st.columns(2)
                with btn1:
                    if pd.notna(job.get('website')) and str(job['website']).strip():
                        st.link_button("🌐 Apply on Website", job['website'], use_container_width=True)
                    else:
                        st.button("Apply", disabled=True, use_container_width=True)
                with btn2:
                    st.button("⭐ Save", key=f"save_{idx}", use_container_width=True)

st.divider()
st.caption("Dataset: https://github.com/BurstSoftware/open-job-postings")
