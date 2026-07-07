import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import json
import requests

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ `openai` package is not installed. Run: `pip install openai`")
    st.stop()

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
    .job-card { 
        background: linear-gradient(145deg, #16213e, #1e2a5c); 
        border-radius: 20px; 
        padding: 24px; 
        margin: 16px 0; 
        border: 1px solid #4a5d9e; 
        transition: all 0.3s ease; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
    }
    .job-card:hover { 
        transform: translateY(-8px); 
        box-shadow: 0 20px 40px rgba(74,93,158,0.4); 
        border-color: #6e8cff; 
    }
    .job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
    .company { color: #8f9eff; font-weight: 600; }
    .badge { display: inline-block; background: #3a4a8c; color: #c0d0ff; padding: 6px 14px; border-radius: 30px; font-size: 0.85rem; margin-right: 10px; margin-bottom: 8px; }
    .header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .dataframe-container { background: #0f1629; border-radius: 16px; padding: 10px; border: 1px solid #334477; }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    
    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", 
                           value=st.session_state.get("nvidia_api_key", ""), 
                           help="Paste your key from https://build.nvidia.com/")
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
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
    st.info("Powered by NVIDIA NIM + GitHub", icon="ℹ️")

# ====================== LOAD JOBS FROM GITHUB ======================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_jobs_from_github():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        # Clean empty id column if needed
        if df.columns[0] == 'Unnamed: 0' or df.iloc[0,0] is None:
            df = df.iloc[:, 1:]
        return df
    except Exception as e:
        st.error(f"Failed to load jobs: {e}")
        # Fallback
        return pd.DataFrame([{
            "title": "Amazon Flex - X", "company": "Amazon", "location": "North Mankato, MN 56003",
            "salary": "$19/hr", "posted": "2026-07-04", "type": "Part Time >19 hours a week",
            "match": 92, "website": "http://amazon.com/getpaid", "phone": "N/a",
            "description": "Picking, packing, sorting, stowing",
            "requirements": "Lifting up to 49lbs, twisting, bending, stooping",
            "benefits": "Benefits available through the A to Z app", "referrer": "narossoh"
        }])

if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs_from_github()

# ====================== OTHER SESSION STATE ======================
if "profile" not in st.session_state:
    st.session_state.profile = pd.DataFrame([{"name": "", "location": "", "experience": "", "skills": "", "education": "", "certifications": ""}])

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}

if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Date", "Company", "Role", "Status", "Fit Score"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# (AGENTS, helper functions, etc. remain the same as your original code)
# ... [Keep all your AGENTS dict, get_nvidia_client, call_nvidia_llm, extract_min_salary functions here] ...

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Discover Jobs", 
    "📊 GitHub Jobs DataFrame",
    "💬 AI Job Assistant", 
    "📝 Profile",
    "🔑 NVIDIA API Guide"
])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2: location_filter = st.selectbox("■ Location", ["All Locations"] + list(st.session_state.jobs['location'].unique()))
    with col3: job_type = st.selectbox("■ Type", ["All Types"] + list(st.session_state.jobs['type'].unique()))
    with col4: min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)
    
    df = st.session_state.jobs.copy()
    # Apply filters...
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False) | 
                df['company'].str.contains(search, case=False, na=False) | 
                df['description'].str.contains(search, case=False, na=False)]
    if location_filter != "All Locations":
        df = df[df['location'].str.contains(location_filter, case=False, na=False)]
    if job_type != "All Types":
        df = df[df['type'] == job_type]
    # ... (rest of filtering same as before)
    
    st.caption(f"Showing **{len(df)}** opportunities from GitHub")
    # Job cards (same as your original)

# ==================== NEW TAB 5: GITHUB DATAFRAME ====================
with tab2:
    st.markdown("### 📊 Live Open Job Postings (GitHub Source)")
    st.caption(f"Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("🔄 Refresh from GitHub", use_container_width=True):
            st.cache_data.clear()
            st.session_state.jobs = load_jobs_from_github()
            st.rerun()
    
    st.dataframe(
        st.session_state.jobs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "website": st.column_config.LinkColumn("Apply"),
            "match": st.column_config.ProgressColumn("Match %", min_value=0, max_value=100)
        }
    )
    
    st.download_button(
        label="📥 Download CSV",
        data=st.session_state.jobs.to_csv(index=False),
        file_name=f"open_job_postings_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# (Keep your other tabs: AI Assistant, Profile, NVIDIA Guide unchanged)

st.caption("Open Job Postings • Live from GitHub • NVIDIA NIM + Multi-Agent AI")
