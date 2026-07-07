import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import json

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (unchanged) ======================
# ... [Your existing CSS stays the same] ...

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    
    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", 
                           value=st.session_state.get("nvidia_api_key", ""))
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!")
        st.rerun()
    
    model_options = ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", 
                     "nvidia/nemotron-4-340b-instruct", "deepseek-ai/deepseek-v3"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    st.divider()
    if st.button("🔄 Refresh Jobs from GitHub", use_container_width=True):
        if "jobs" in st.session_state:
            del st.session_state.jobs
        st.success("Jobs refreshed!")
        st.rerun()
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "profile", "applications", "candidate_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ====================== LOAD JOBS FROM GITHUB ======================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_jobs_from_github():
    # ←←← CHANGE THIS URL TO YOUR GITHUB RAW CSV LINK
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/jobs.csv"
    
    try:
        df = pd.read_csv(GITHUB_CSV_URL)
        
        # Auto-generate ID if missing
        if 'id' not in df.columns or df['id'].isna().all():
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        else:
            df['id'] = df['id'].fillna(str(uuid.uuid4()))
            
        return df
    except Exception as e:
        st.error(f"❌ Failed to load jobs from GitHub: {e}")
        st.info("Make sure your CSV is publicly accessible and the URL is a **raw** GitHub link.")
        return pd.DataFrame()

# Load jobs
if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs_from_github()

# ====================== OTHER SESSION STATE (unchanged) ======================
if "profile" not in st.session_state:
    st.session_state.profile = pd.DataFrame([{"name": "", "location": "", "experience": "", "skills": "", "education": "", "certifications": ""}])

# ... [Keep the rest of your AGENTS, helper functions, etc. unchanged] ...

# ====================== DISCOVER JOBS TAB (Small Update) ======================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    
    # Add GitHub source info
    st.caption(f"📡 Loaded from GitHub • {len(st.session_state.jobs)} total opportunities")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2: location_filter = st.selectbox("■ Location", ["All Locations"] + sorted(st.session_state.jobs['location'].dropna().unique().tolist()))
    with col3: job_type = st.selectbox("■ Type", ["All Types"] + sorted(st.session_state.jobs['type'].dropna().unique().tolist()))
    with col4: min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)
    
    df = st.session_state.jobs.copy()
    
    # ... [Keep your existing filtering logic] ...
    
    st.caption(f"Showing **{len(df)}** opportunities")
    if df.empty:
        st.warning("No jobs match your filters.")
    else:
        for _, job in df.iterrows():
            st.html(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="job-title">{job['title']}</div>
                        <div class="company">■ {job['company']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.2rem; font-weight:700; color:#00ff9d;">{job['salary']}</div>
                        <div style="color:#8899cc;">{job['location']}</div>
                    </div>
                </div>
                <div style="margin: 20px 0 16px 0; display: flex; flex-wrap: wrap; gap: 12px;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <span class="badge">Match: {job.get('match', 85)}%</span>
                </div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;"><strong>Description:</strong> {job.get('description','')}</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;"><strong>Requirements:</strong> {job.get('requirements','')}</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;"><strong>Benefits:</strong> {job.get('benefits','')}</div>
                <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply Now</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """)
