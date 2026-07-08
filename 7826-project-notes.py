import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import json

# Try to import OpenAI (used as client for NVIDIA NIM)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ `openai` package is not installed. Run: `pip install openai`")
    st.stop()

# ====================== CONFIG ======================
# Tool: Streamlit
# Functionality: Configure the overall page appearance and layout
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",                    # Wide layout for better use of screen space
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
# Tool: Streamlit + HTML/CSS
# Functionality: Custom styling for modern dark UI, job cards, chat bubbles, agent cards, etc.
st.markdown("""
<style>
    ... (all the CSS styles) ...
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
# Tool: Streamlit Sidebar
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    
    st.subheader("🔑 NVIDIA NIM Settings")
    
    # Functionality: Store and manage NVIDIA API key in session state
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", 
                           type="password", 
                           value=st.session_state.get("nvidia_api_key", ""),
                           help="Paste your key from https://build.nvidia.com/")
    
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()
    
    # Model selection for NVIDIA NIM
    model_options = ["meta/llama-3.1-70b-instruct", 
                     "meta/llama-3.1-405b-instruct", 
                     "nvidia/nemotron-4-340b-instruct", 
                     "deepseek-ai/deepseek-v3"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    
    # Temperature control for LLM creativity
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    st.divider()
    
    # Clear all session data button
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "profile", "applications", "candidate_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.info("Powered by NVIDIA NIM", icon="ℹ️")

# ====================== INITIAL DATA ======================
# Tool: Pandas + Streamlit Session State + UUID
# Functionality: Initialize in-memory job database and user data if not present

if "jobs" not in st.session_state:
    jobs_list = [
        {
            "id": str(uuid.uuid4()),           # Unique identifier for each job
            "title": "Amazon Flex - X",
            # ... other job fields
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

# Initialize empty profile, candidate data, applications, and chat history
if "profile" not in st.session_state:
    st.session_state.profile = pd.DataFrame([{"name": "", "location": "", ...}])

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}

if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Date", "Company", "Role", "Status", "Fit Score"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== AGENTS ======================
# Functionality: Define multi-agent system (different AI specialists)
# Each agent has its own system prompt and personality
AGENTS = {
    "🎯 Job Match Analyst": {
        "emoji": "📊",
        "description": "...",
        "system": "You are an expert job-market analyst..."   # System prompt for LLM
    },
    # ... other 5 agents (CV Tailor, Cover Letter, Interview Coach, etc.)
}

# ====================== HELPER FUNCTIONS ======================

def get_nvidia_client():
    """Tool: OpenAI Python client (configured for NVIDIA NIM)
    Functionality: Creates authenticated client for NVIDIA API"""
    if not st.session_state.get("nvidia_api_key"):
        st.warning("⚠️ Please enter your NVIDIA API Key...")
        return None
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1", 
        api_key=st.session_state.nvidia_api_key
    )

def call_nvidia_llm(messages, temperature=None):
    """Tool: NVIDIA NIM via OpenAI compatible API
    Functionality: Sends messages to selected LLM and returns response"""
    client = get_nvidia_client()
    if not client: 
        return "❌ Please provide a valid NVIDIA API key."
    
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
    """Tool: Regex (re)
    Functionality: Extracts numeric salary value from salary string for filtering"""
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

# Create 4 main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Discover Jobs", 
    "💬 AI Job Assistant", 
    "📝 Profile",
    "🔑 NVIDIA API Guide"
])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    # Functionality: Job search and filtering interface
    # Tools: Pandas filtering + Streamlit widgets + Custom HTML cards
    st.markdown("### ■ Discover Your Next Role")
    
    # Search and filter controls
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1: search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    # ... other filters (location, type, min salary)
    
    # Apply filters to pandas DataFrame
    df = st.session_state.jobs.copy()
    # ... filtering logic using .str.contains() and custom salary extractor
    
    # Display jobs as beautiful custom cards using HTML + CSS
    for _, job in df.iterrows():
        st.markdown(f"""<div class="job-card"> ... </div>""", unsafe_allow_html=True)

# ==================== TAB 2: AI JOB ASSISTANT ====================
with tab2:
    # Functionality: Multi-Agent Chat Interface
    # Tools: Streamlit chat + NVIDIA NIM LLM + Session State
    
    # Agent selector
    selected_agent_name = st.selectbox("Select Specialist", list(AGENTS.keys()))
    agent = AGENTS[selected_agent_name]
    
    # Show agent info card
    st.markdown(f"""<div class="agent-info"> ... </div>""", unsafe_allow_html=True)
    
    # Display chat history with custom styling
    for msg in st.session_state.chat_history:
        # Render user vs AI messages differently
        ...
    
    # Chat input handling
    if prompt := st.chat_input("Describe the job or what you need help with..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner(f"{agent['emoji']} {selected_agent_name} is thinking..."):
            # Prepare rich context (jobs + profile)
            context = {
                "current_jobs": st.session_state.jobs.to_dict(orient="records"),
                "candidate_profile": st.session_state.profile.iloc[0].to_dict(),
                ...
            }
            
            # Call NVIDIA LLM with agent-specific system prompt
            response = call_nvidia_llm([
                {"role": "system", "content": agent["system"]},
                {"role": "user", "content": full_prompt}
            ])
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()

# ==================== TAB 3: PROFILE ====================
with tab3:
    # Functionality: User profile management
    # Tools: Streamlit Form + Pandas + Download button
    profile_form = st.form("profile_form")
    # ... input fields for name, experience, skills, etc.
    
    if submit_button:
        # Update session state DataFrame
        st.session_state.profile[...] = ...
        st.success("Profile saved!")

    # Allow downloading profile as CSV
    st.download_button("Download Profile", 
                      data=st.session_state.profile.to_csv(index=False), 
                      file_name="profile.csv")

# ==================== TAB 4: NVIDIA API GUIDE ====================
with tab4:
    # Functionality: Step-by-step guide for getting NVIDIA API key
    # Pure informational content with custom styled steps
    ...

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant")
