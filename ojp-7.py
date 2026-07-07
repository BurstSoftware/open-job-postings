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

# ====================== CUSTOM CSS (Updated for screenshot style) ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
    .header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    
    .job-card {
        background: linear-gradient(145deg, #1e2a5c, #16213e);
        border-radius: 20px;
        padding: 28px;
        margin: 20px 0;
        border: 1px solid #4a6bff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .job-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 40px rgba(74, 107, 255, 0.3);
        border-color: #6e8cff;
    }
    .job-title { font-size: 1.65rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
    .company { color: #a0c4ff; font-weight: 600; font-size: 1.1rem; }
    .salary { font-size: 1.5rem; font-weight: 700; color: #00ff9d; }
    .location { color: #8899cc; font-size: 1rem; }
    .badge {
        display: inline-block;
        background: #3a4a8c;
        color: #c0d0ff;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        margin-right: 10px;
        margin-bottom: 8px;
    }
    .section-title { color: #b0b8ff; font-weight: 600; margin-top: 18px; font-size: 1.05rem; }
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
    if st.button("🔄 Refresh Jobs from GitHub", use_container_width=True):
        if "jobs" in st.session_state:
            del st.session_state.jobs
        st.success("Jobs refreshed from GitHub!")
        st.rerun()
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "profile", "applications", "candidate_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.info("Powered by NVIDIA NIM + GitHub", icon="ℹ️")

# ====================== LOAD JOBS FROM GITHUB ======================
@st.cache_data(ttl=300)
def load_jobs_from_github():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
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

if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs_from_github()

# ====================== SESSION STATE ======================
if "profile" not in st.session_state:
    st.session_state.profile = pd.DataFrame([{"name": "", "location": "", "experience": "", "skills": "", "education": "", "certifications": ""}])

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}

if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Date", "Company", "Role", "Status", "Fit Score"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== AGENTS ======================
AGENTS = {
    "🎯 Job Match Analyst": {
        "emoji": "📊",
        "description": "Analyzes how well a job matches your profile and gives fit scores with improvement tips.",
        "system": "You are an expert job-market analyst. Score job fit (0-100), highlight must-have vs nice-to-have matches..."
    },
    "📝 CV Tailor": {
        "emoji": "📄",
        "description": "Expert CV writer that tailors your resume to specific job descriptions...",
        "system": "You are a world-class CV writer..."
    },
    "✉️ Cover Letter Writer": {
        "emoji": "💌",
        "description": "Creates personalized, compelling cover letters...",
        "system": "You write compelling, non-generic cover letters..."
    },
    "🧠 Interview Coach": {
        "emoji": "🎤",
        "description": "Prepares you for interviews with STAR method answers...",
        "system": "You are a STAR-method interview coach..."
    },
    # Add the remaining agents as needed
}

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.warning("⚠️ Please enter your NVIDIA API Key in the sidebar.")
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=st.session_state.nvidia_api_key)

def call_nvidia_llm(messages, temperature=None):
    client = get_nvidia_client()
    if not client: return "❌ Please provide a valid NVIDIA API key."
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("selected_model"),
            messages=messages,
            temperature=temperature or st.session_state.get("temperature", 0.7),
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ NVIDIA API Error: {str(e)}"

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Discovery Jobs", 
    "💬 AI Job Assistant", 
    "📝 Profile",
    "🔑 NVIDIA API Guide"
])

# ==================== TAB 1: DISCOVERY JOBS (New Card Design) ====================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("🔍 Search...", placeholder="Amazon Flex, warehouse")
    with col2: 
        locations = ["All Locations"] + list(st.session_state.jobs['location'].dropna().unique())
        location_filter = st.selectbox("📍 Location", locations)
    with col3: 
        types = ["All Types"] + list(st.session_state.jobs['type'].dropna().unique())
        job_type = st.selectbox("📋 Type", types)
    with col4: 
        min_salary = st.slider("💰 Min Hourly ($)", 0, 200, 15)
    
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
    
    st.caption(f"Showing **{len(df)}** opportunities")
    
    if df.empty:
        st.warning("No jobs match your filters.")
    else:
        for _, job in df.iterrows():
            st.html(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="job-title">{job.get('title', 'N/A')}</div>
                        <div class="company">■ {job.get('company', 'N/A')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="salary">{job.get('salary', 'N/A')}</div>
                        <div class="location">{job.get('location', 'N/A')}</div>
                    </div>
                </div>

                <div style="margin: 24px 0 18px 0; display: flex; flex-wrap: wrap; gap: 10px;">
                    <span class="badge">{job.get('type', 'N/A')}</span>
                    <span class="badge">Posted {job.get('posted', 'N/A')}</span>
                    <span class="badge">Match: {job.get('match', 85)}%</span>
                </div>

                <div class="section-title">Description:</div>
                <div style="color:#d0d8ff; line-height:1.6;">{job.get('description','N/A')}</div>
                
                <div class="section-title">Requirements:</div>
                <div style="color:#d0d8ff; line-height:1.6;">{job.get('requirements','N/A')}</div>
                
                <div class="section-title">Benefits:</div>
                <div style="color:#d0d8ff; line-height:1.6;">{job.get('benefits','N/A')}</div>

                <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334477; display: flex; gap: 30px; font-size: 1rem;">
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply Now</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                    <div><strong>Referrer:</strong> {job.get('referrer','N/A')}</div>
                </div>
            </div>
            """)

# ==================== TAB 2: AI JOB ASSISTANT ====================
with tab2:
    st.markdown("### 💬 AI Job Assistant — Multi-Agent Studio")
    # Paste your full original AI Assistant code here (agent selector, chat, etc.)

# ==================== TAB 3: PROFILE ====================
with tab3:
    st.markdown("### 📝 Profile")
    # Paste your original Profile code here

# ==================== TAB 4: NVIDIA API GUIDE ====================
with tab4:
    st.markdown("### 🔑 How to Create Your NVIDIA API Key")
    # Paste your original NVIDIA Guide code here

st.caption("Open Job Postings • Live from GitHub • NVIDIA NIM + Multi-Agent AI Assistant")
