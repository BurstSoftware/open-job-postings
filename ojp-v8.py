import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re

# Try to import OpenAI for NVIDIA NIM
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ====================== CONFIGURATION ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
    .header-title {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #a0c4ff, #c0d0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
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
    .job-title { font-size: 1.45rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
    .company { color: #8f9eff; font-weight: 600; font-size: 1.1rem; margin-bottom: 12px; }
    .salary { font-size: 1.3rem; font-weight: 700; color: #00ff9d; text-align: right; }
    .location { color: #8899cc; text-align: right; font-size: 0.95rem; }
    .badge {
        display: inline-block; background: #3a4a8c; color: #c0d0ff;
        padding: 6px 14px; border-radius: 30px; font-size: 0.85rem;
        margin-right: 10px; margin-bottom: 8px;
    }
    .job-section { color: #b0b8ff; line-height: 1.6; margin-bottom: 16px; }
    .job-section strong { color: #a0c4ff; }
    .chat-message {
        padding: 16px 22px; border-radius: 20px; margin: 14px 0;
        max-width: 85%; box-shadow: 0 5px 20px rgba(0,0,0,0.25);
    }
    .user-msg { background: linear-gradient(135deg, #4a6bff, #2a4fff); color: white; margin-left: auto; }
    .ai-msg { background: linear-gradient(145deg, #1e2a5c, #16213e); color: #e0e0ff; margin-right: auto; border: 1px solid #445588; }
</style>
""", unsafe_allow_html=True)

# ====================== DATA LOADING ======================
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
        return pd.DataFrame(columns=expected_cols)

df = load_jobs_from_github()

# ====================== HELPER FUNCTIONS ======================
def format_posted_date(posted_date):
    if pd.isna(posted_date):
        return "N/A"
    return posted_date.strftime("%b %d, %Y")

def display_job_card(job):
    st.html(f"""
    <div class="job-card">
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div style="flex:1;">
                <div class="job-title">{job.get('title', 'N/A')}</div>
                <div class="company">■ {job.get('company', 'N/A')}</div>
            </div>
            <div style="text-align:right; min-width:180px;">
                <div class="salary">{job.get('salary', 'N/A')}</div>
                <div class="location">{job.get('location', 'N/A')}</div>
            </div>
        </div>
        <div style="margin:20px 0 16px 0; display:flex; flex-wrap:wrap; gap:12px;">
            <span class="badge">{job.get('type', 'N/A')}</span>
            <span class="badge">Match: {int(job.get('match', 0))}%</span>
            <span class="badge">Posted: {format_posted_date(job.get('posted'))}</span>
        </div>
        <div class="job-section"><strong>Description:</strong> {job.get('description', 'No description provided.')}</div>
        <div class="job-section"><strong>Requirements:</strong> {job.get('requirements', 'Not specified.')}</div>
        <div class="job-section"><strong>Benefits:</strong> {job.get('benefits', 'Not specified.')}</div>
        <div class="job-footer" style="display:flex; gap:24px; font-size:0.95rem; color:#8899cc; border-top:1px solid #334477; padding-top:14px;">
            <div><strong>Website:</strong> <a href="{job.get('website', '#')}" target="_blank">Apply Now →</a></div>
            <div><strong>Phone:</strong> {job.get('phone', 'N/A')}</div>
            <div><strong>Referrer:</strong> {job.get('referrer', 'N/A')}</div>
        </div>
    </div>
    """)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 💼 **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()

    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", 
                           value=st.session_state.get("nvidia_api_key", ""),
                           help="Get key from https://build.nvidia.com/")
    
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!")
        st.rerun()

    model_options = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3"
    ]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")

    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ====================== SESSION STATE ======================
if "jobs" not in st.session_state:
    st.session_state.jobs = df if not df.empty else pd.DataFrame([{
        "id": str(uuid.uuid4()), "title": "Amazon Flex - X", "company": "Amazon",
        "location": "North Mankato, MN", "salary": "$19/hr", "posted": "2026-07-04",
        "type": "Part Time", "match": 92, "website": "http://amazon.com/getpaid",
        "phone": "N/A", "description": "Picking, packing...", "requirements": "Lifting up to 49lbs",
        "benefits": "Benefits via A to Z app", "referrer": "narossoh"
    }])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== AGENTS ======================
AGENTS = { ... }  # (your original AGENTS dict - kept as-is)

# ====================== NVIDIA LLM ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.warning("Please enter NVIDIA API Key")
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=st.session_state.nvidia_api_key)

def call_nvidia_llm(messages, temperature=None):
    client = get_nvidia_client()
    if not client: return "❌ No API key provided."
    try:
        resp = client.chat.completions.create(
            model=st.session_state.selected_model,
            messages=messages,
            temperature=temperature or st.session_state.get("temperature", 0.7),
            max_tokens=2048
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
st.markdown("Discover real opportunities from the community dataset")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Discover Jobs",
    "💬 AI Job Assistant",
    "📋 My Applications",
    "👤 Profile"
])

with tab1:
    st.subheader("Available Jobs")
    search = st.text_input("Search jobs...", "")
    filtered = st.session_state.jobs
    if search:
        filtered = filtered[filtered.apply(lambda x: search.lower() in str(x).lower(), axis=1)]
    
    for _, job in filtered.iterrows():
        display_job_card(job)

with tab2:
    st.subheader("AI Job Assistant")
    agent_name = st.selectbox("Choose Assistant", list(AGENTS.keys()))
    
    for msg in st.session_state.chat_history:
        st.markdown(f'<div class="chat-message {"user-msg" if msg["role"]=="user" else "ai-msg"}">{msg["content"]}</div>', unsafe_allow_html=True)
    
    user_input = st.chat_input("Ask anything about jobs, CVs, interviews...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            response = call_nvidia_llm([
                {"role": "system", "content": AGENTS[agent_name]["system"]},
                {"role": "user", "content": user_input}
            ])
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# Add the other tabs (My Applications, Profile) as needed...

st.caption("Powered by NVIDIA NIM • Community Job Dataset")
