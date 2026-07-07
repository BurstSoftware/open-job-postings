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

    .agent-info {
        background: linear-gradient(145deg, #1e2a5c, #16213e); 
        border-radius: 16px; 
        padding: 18px 24px; 
        border: 1px solid #445588;
        margin: 15px 0 25px 0;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .agent-info-emoji { font-size: 2.2rem; }
    .agent-title { font-size: 1.25rem; font-weight: 700; color: #a0c4ff; }
    
    .chat-container {
        background: #0f1629;
        border-radius: 20px;
        padding: 24px;
        border: 1px solid #334477;
        min-height: 520px;
        overflow-y: auto;
    }
    .chat-message {
        padding: 16px 22px;
        border-radius: 20px;
        margin: 14px 0;
        max-width: 85%;
        box-shadow: 0 5px 20px rgba(0,0,0,0.25);
    }
    .user-msg { background: linear-gradient(135deg, #4a6bff, #2a4fff); color: white; margin-left: auto; border-bottom-right-radius: 6px; }
    .ai-msg { background: linear-gradient(145deg, #1e2a5c, #16213e); color: #e0e0ff; margin-right: auto; border: 1px solid #445588; border-bottom-left-radius: 6px; }

    .guide-step {
        background: linear-gradient(145deg, #16213e, #1e2a5c);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border-left: 5px solid #6e8cff;
    }
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
    "🎯 Job Match Analyst": {"emoji": "📊", "description": "Analyzes how well a job matches your profile...", "system": "..."},
    # ... (keep all your original agents here)
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

# ==================== TAB 1: DISCOVERY JOBS (Job Cards) ====================
with tab1:
    st.markdown("### 🔍 Discovery Jobs — Live from GitHub")
    st.caption(f"Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Showing **{len(st.session_state.jobs)}** opportunities")
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("🔄 Refresh from GitHub", use_container_width=True):
            st.cache_data.clear()
            st.session_state.jobs = load_jobs_from_github()
            st.rerun()
    
    df = st.session_state.jobs.copy()
    
    if df.empty:
        st.warning("No jobs found.")
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
                        <div style="font-size:1.2rem; font-weight:700; color:#00ff9d;">{job.get('salary', 'N/A')}</div>
                        <div style="color:#8899cc;">{job.get('location', 'N/A')}</div>
                    </div>
                </div>
                <div style="margin: 20px 0 16px 0; display: flex; flex-wrap: wrap; gap: 12px;">
                    <span class="badge">{job.get('type', 'N/A')}</span>
                    <span class="badge">Posted {job.get('posted', 'N/A')}</span>
                    <span class="badge">Match: {job.get('match', 85)}%</span>
                </div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;"><strong>Description:</strong> {job.get('description','N/A')}</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;"><strong>Requirements:</strong> {job.get('requirements','N/A')}</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;"><strong>Benefits:</strong> {job.get('benefits','N/A')}</div>
                <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply Now</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """)

# ==================== TAB 2: AI JOB ASSISTANT ====================
with tab2:
    st.markdown("### 💬 AI Job Assistant — Multi-Agent Studio")
    # Paste your full original AI Job Assistant code here (the one with agent selector, chat, etc.)
    # ... (unchanged from your previous version)

# ==================== TAB 3 & 4 (Profile + NVIDIA Guide) ====================
# Paste your original Tab 3 and Tab 4 code here

st.caption("Open Job Postings • Live from GitHub • NVIDIA NIM + Multi-Agent AI Assistant")
