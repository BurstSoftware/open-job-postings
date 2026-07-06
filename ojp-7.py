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
        background: #16213e;
        padding: 18px 22px;
        border-radius: 16px;
        margin: 12px 0;
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
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", 
                           value=st.session_state.get("nvidia_api_key", ""), 
                           help="Get your key from https://build.nvidia.com/")
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()
    
    model_options = ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", 
                     "nvidia/nemotron-4-340b-instruct", "deepseek-ai/deepseek-v3"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    st.divider()
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "profile", "applications", "candidate_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.info("Powered by NVIDIA NIM", icon="ℹ️")

# ====================== INITIAL DATA ======================
if "jobs" not in st.session_state:
    jobs_list = [
        {
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
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

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
    "📝 CV Tailor": {"emoji": "📄", "description": "Expert CV writer...", "system": "..."},
    "✉️ Cover Letter Writer": {"emoji": "💌", "description": "Creates personalized cover letters...", "system": "..."},
    "🧠 Interview Coach": {"emoji": "🎤", "description": "Prepares you for interviews...", "system": "..."},
    "📈 Salary & Negotiation": {"emoji": "💰", "description": "Provides salary benchmarks...", "system": "..."},
    "🚀 Upskill Advisor": {"emoji": "📚", "description": "Identifies skill gaps...", "system": "..."}
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

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "📝 Profile", "📖 Setup Guide"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    # (Your existing code - unchanged)
    st.markdown("### ■ Discover Your Next Role")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2: location_filter = st.selectbox("■ Location", ["All Locations", "North Mankato"])
    with col3: job_type = st.selectbox("■ Type", ["All Types", "Part Time >19 hours a week"])
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
    
    st.caption(f"Showing **{len(df)}** opportunities")
    if df.empty:
        st.warning("No jobs match your filters.")
    else:
        for _, job in df.iterrows():
            st.html(f"""<div class="job-card"> ... </div>""")  # (kept your card HTML)

# ==================== TAB 2 & 3 (unchanged) ====================
# ... (your existing Tab 2 and Tab 3 code goes here) ...

# ==================== NEW TAB 4: SETUP GUIDE ====================
with tab4:
    st.markdown("### 📖 How to Create Your NVIDIA API Key")
    st.markdown("Follow these steps to get your free NVIDIA NIM API key:")

    steps = [
        ("1. Create / Sign In", "Go to [build.nvidia.com](https://build.nvidia.com/) or [ngc.nvidia.com](https://ngc.nvidia.com/) and sign in with your NVIDIA account (or create one)."),
        ("2. Go to API Keys", "Click your profile icon → **Settings** → **API Keys** (or visit [org.ngc.nvidia.com/account/api-keys](https://org.ngc.nvidia.com/account/api-keys))."),
        ("3. Generate Key", "Click **Generate Personal Key** (or **Generate API Key**)."),
        ("4. Configure", "Add a description, select **NGC Catalog** under Services, set expiration (Never expires is fine for personal use)."),
        ("5. Copy Key", "Copy the key (starts with `nvapi-...`). Paste it in the sidebar."),
    ]

    for icon, text in steps:
        st.markdown(f"""
        <div class="guide-step">
            <h4>{icon}</h4>
            <p>{text}</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("💡 **Tip**: After pasting the key in the sidebar, you can immediately start using the AI assistants!", icon="🔑")
    st.caption("Need help? The key gives you access to powerful models like Llama 3.1, Nemotron, etc.")

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant • Maintained with ❤️")
