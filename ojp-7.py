import streamlit as st
import pandas as pd
import uuid
import re
import json
from io import StringIO

try:
    from openai import OpenAI
except ImportError:
    st.error("❌ `openai` package is not installed.")
    st.stop()

# ====================== CONFIG ======================
st.set_page_config(page_title="Open Job Postings • AI Powered", page_icon="■", layout="wide")

# ====================== CUSTOM CSS (your original) ======================
st.markdown("""<style>
    .main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
    .job-card { background: linear-gradient(145deg, #16213e, #1e2a5c); border-radius: 20px; padding: 24px; margin: 16px 0; border: 1px solid #4a5d9e; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .job-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(74,93,158,0.4); border-color: #6e8cff; }
    .job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
    .company { color: #8f9eff; font-weight: 600; }
    .badge { display: inline-block; background: #3a4a8c; color: #c0d0ff; padding: 6px 14px; border-radius: 30px; font-size: 0.85rem; margin-right: 10px; margin-bottom: 8px; }
    .header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
</style>""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key", type="password", value=st.session_state.get("nvidia_api_key", ""))
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!")
        st.rerun()
    
    st.session_state.selected_model = st.selectbox("Select Model", 
        ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", "nvidia/nemotron-4-340b-instruct"], index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    if st.button("🔄 Refresh Jobs from GitHub", use_container_width=True):
        if "jobs" in st.session_state: del st.session_state.jobs
        st.rerun()

# ====================== LOAD FROM GITHUB ======================
GITHUB_CSV_URL = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"

@st.cache_data(ttl=60)
def load_jobs():
    try:
        df = pd.read_csv(GITHUB_CSV_URL)
        
        # Fix ID column
        df['id'] = df['id'].astype(str).str.strip()
        df['id'] = df['id'].replace(['', 'nan', 'NaN'], None)
        
        missing = df['id'].isna()
        if missing.any():
            df.loc[missing, 'id'] = [str(uuid.uuid4()) for _ in range(missing.sum())]
        
        df['match'] = pd.to_numeric(df['match'], errors='coerce').fillna(85)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load from GitHub: {e}")
        return pd.DataFrame()

if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs()

# ====================== TABS ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "📝 Profile", "🔑 NVIDIA API Guide"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    st.caption(f"📡 Loaded **{len(st.session_state.jobs)}** opportunities from GitHub")

    # Filters
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2: location_filter = st.selectbox("■ Location", ["All Locations"] + sorted(st.session_state.jobs['location'].dropna().unique().tolist()))
    with col3: job_type = st.selectbox("■ Type", ["All Types"] + sorted(st.session_state.jobs['type'].dropna().unique().tolist()))
    with col4: min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)

    df = st.session_state.jobs.copy()
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False) | 
                df['company'].str.contains(search, case=False, na=False) | 
                df['description'].str.contains(search, case=False, na=False)]
    if location_filter != "All Locations":
        df = df[df['location'].str.contains(location_filter, case=False, na=False)]
    if job_type != "All Types":
        df = df[df['type'] == job_type]
    
    def extract_min_salary(s):
        nums = re.findall(r'\d+', str(s))
        return int(nums[0]) if nums else 0
    df = df[df['salary'].apply(extract_min_salary) >= min_salary]

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
                    <span class="badge">Match: {int(job.get('match', 85))}%</span>
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

# ==================== Remaining Tabs (Add your original code) ====================
# Paste your original Tab 2, Tab 3, and Tab 4 code here

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant")
