# Complete Updated Codebase with Enhanced "Post a Job" Tab

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

# ====================== CUSTOM CSS (Enhanced for Employers Tab) ======================
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

    /* Agent Info */
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

    /* Guide Styling */
    .guide-step {
        background: linear-gradient(145deg, #16213e, #1e2a5c);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border-left: 5px solid #6e8cff;
        color: white;
    }

    /* Enhanced Employers Section */
    .employer-card {
        background: linear-gradient(145deg, #16213e, #1e2a5c);
        border-radius: 20px;
        padding: 32px;
        border: 2px solid #6e8cff;
        box-shadow: 0 15px 35px rgba(110, 140, 255, 0.15);
        transition: all 0.3s ease;
    }
    .employer-card:hover {
        border-color: #00ff9d;
        transform: translateY(-5px);
    }
    .req-item {
        background: rgba(58, 74, 140, 0.4);
        padding: 12px 18px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #6e8cff;
    }
    .big-button {
        background: linear-gradient(90deg, #00ff9d, #00cc7a);
        color: #0f0f23;
        font-size: 1.35rem;
        font-weight: 700;
        padding: 20px 60px;
        border: none;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 255, 157, 0.3);
    }
    .big-button:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(0, 255, 157, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR (unchanged) ======================
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

# ====================== INITIAL DATA (unchanged) ======================
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

# ====================== AGENTS, HELPERS (unchanged) ======================
AGENTS = { ... }  # (kept exactly the same - omitted for brevity)

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Discover Jobs", 
    "💬 AI Job Assistant", 
    "📝 Profile",
    "🔑 NVIDIA API Guide",
    "💼 Post a Job • Employers"
])

# Tabs 1-4 remain completely unchanged (omitted for brevity)

# ==================== TAB 5: POST A JOB (BEAUTIFIED) ====================
with tab5:
    st.markdown('<h2 style="color:#a0c4ff;">💼 Get Your Job Listed on Open Job Postings</h2>', unsafe_allow_html=True)
    
    # Premium Pricing Box (already beautiful)
    st.markdown("""
    <div style="background: linear-gradient(145deg, #16213e, #1e2a5c); 
                border-radius: 20px; padding: 32px; text-align: center; 
                border: 2px solid #6e8cff; margin: 20px 0;">
        <h3 style="color:#00ff9d; margin-bottom:8px;">$49 / Month • Featured Listing</h3>
        <p style="font-size:1.1rem; color:#c0d0ff;">
            Reach qualified candidates with zero spam. Your job stays live for 30 days.
        </p>
        <div style="margin: 24px 0; font-size:1.3rem; color:#a0c4ff;">
            ✅ Listed on homepage • ✅ AI matching • ✅ Direct applications
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### How It Works")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""<div class="guide-step"><h4>1. Submit Form</h4><p>Fill out the details below or use our Google Form.</p></div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class="guide-step"><h4>2. Review & Approve</h4><p>We review your posting (usually within 24h).</p></div>""", unsafe_allow_html=True)
    with col_c:
        st.markdown("""<div class="guide-step"><h4>3. Pay & Go Live</h4><p>Receive invoice via email. Job goes live after payment.</p></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ====================== BEAUTIFIED SUBMISSION SECTION ======================
    st.subheader("🚀 Quickest Way: Submit via Google Form")
    
    st.markdown("""
    <div class="employer-card" style="text-align:center; margin: 30px 0;">
        <a href="https://forms.gle/Yjzx9cbrMWZ6mrA58" target="_blank">
            <button class="big-button">
                📋 Submit Job Posting Now ($49/month)
            </button>
        </a>
        <p style="margin-top: 20px; color:#b0b8ff; font-size:1.05rem;">
            You will be redirected to a secure Google Form.<br>
            After submission we will contact you to confirm details and send the invoice.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Required Information - Now Beautiful
    st.markdown("### Required Information")
    req_items = [
        "Job Title", "Company Name", "Work Location", "Salary / Compensation",
        "Job Posted Date", "Job Type", "Website / Application Link", "Phone Number",
        "Job Description", "Job Requirements", "Job Benefits", "Job Referrer (optional)",
        "Your Name (contact)", "Your Phone Number", "Your Email Address", "Best Time to Reach You"
    ]
    
    cols = st.columns(3)
    for i, item in enumerate(req_items):
        with cols[i % 3]:
            st.markdown(f'<div class="req-item">• {item}</div>', unsafe_allow_html=True)

    st.info("💡 All submissions are manually reviewed for quality before going live.", icon="🔍")

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant • Employers: $49/month listings")
