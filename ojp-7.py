import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import json

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
    
    /* Job Cards */
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
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", value=st.session_state.get("nvidia_api_key", ""), help="Paste your key from https://build.nvidia.com/")
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()
    
    model_options = ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", "nvidia/nemotron-4-340b-instruct", "deepseek-ai/deepseek-v3"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    st.divider()
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "profile", "applications", "candidate_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.info("Powered by NVIDIA NIM", icon="ℹ️")

# ====================== LOAD JOBS FROM CSV ======================
@st.cache_data(ttl=3600)  # Refresh every hour
def load_jobs_from_csv():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        # Clean up empty id column if needed
        if 'id' in df.columns and df['id'].isna().all():
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        elif 'id' not in df.columns:
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        return df
    except Exception as e:
        st.error(f"Failed to load jobs from GitHub: {e}")
        # Fallback with the original single job
        return pd.DataFrame([{
            "id": str(uuid.uuid4()),
            "title": "Amazon Flex - X",
            "company": "Amazon",
            "location": "North Mankato, MN 56003",
            "salary": "$19/hr",
            "posted": "2026-07-04",
            "type": "Part Time >19 hours a week",
            "match": 92,
            "website": "http://amazon.com/getpaid",
            "phone": "N/a",
            "description": "Picking, packing, sorting, stowing",
            "requirements": "Lifting up to 49lbs, twisting, bending, stooping",
            "benefits": "Benefits available through the A to Z app",
            "referrer": "narossoh"
        }])

# Initialize jobs from CSV
if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs_from_csv()

# ====================== OTHER INITIAL DATA ======================
if "profile" not in st.session_state:
    st.session_state.profile = pd.DataFrame([{"name": "", "location": "", "experience": "", "skills": "", "education": "", "certifications": ""}])

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}

if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Date", "Company", "Role", "Status", "Fit Score"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== AGENTS & HELPERS (unchanged) ======================
# ... [Keep all your AGENTS dictionary, get_nvidia_client, call_nvidia_llm, extract_min_salary functions as they are] ...

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Discover Jobs", 
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
    
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False) | 
                df['company'].str.contains(search, case=False, na=False) | 
                df['description'].str.contains(search, case=False, na=False)]
    
    if location_filter != "All Locations":
        df = df[df['location'].str.contains(location_filter, case=False, na=False)]
    if job_type != "All Types":
        df = df[df['type'] == job_type]
    
    df = df[df['salary'].apply(extract_min_salary) >= min_salary]
    
    st.caption(f"Showing **{len(df)}** opportunities from GitHub CSV")
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

# (The rest of your tabs 2, 3, 4 remain exactly the same)
