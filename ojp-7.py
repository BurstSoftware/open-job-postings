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
    .job-card { background: linear-gradient(145deg, #16213e, #1e2a5c); border-radius: 20px; padding: 24px; margin: 16px 0; border: 1px solid #4a5d9e; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .job-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(74,93,158,0.4); border-color: #6e8cff; }
    .job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
    .company { color: #8f9eff; font-weight: 600; }
    .badge { display: inline-block; background: #3a4a8c; color: #c0d0ff; padding: 6px 14px; border-radius: 30px; font-size: 0.85rem; margin-right: 10px; margin-bottom: 8px; }
    .header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .chat-message { padding: 14px 18px; border-radius: 18px; margin: 10px 0; max-width: 85%; }
    .user-msg { background: linear-gradient(135deg, #4a6bff, #2a4fff); color: white; margin-left: auto; }
    .ai-msg { background: #16213e; color: #e0e0ff; margin-right: auto; border: 1px solid #334477; }
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
    
    model_options = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3"
    ]
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
    st.session_state.profile = pd.DataFrame([{
        "name": "", "location": "", "experience": "", 
        "skills": "", "education": "", "certifications": ""
    }])

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
        "system": "You are an expert job-market analyst. Score job fit (0-100), highlight must-have vs nice-to-have matches, red flags, and suggest exact tailoring strategies based on the candidate profile."
    },
    "📝 CV Tailor": {
        "emoji": "📄",
        "system": "You are a world-class CV writer specialized in modern tailoring. Convert achievements into strong bullet points using action verbs. Optimize for ATS."
    },
    "✉️ Cover Letter Writer": {
        "emoji": "💌",
        "system": "You write compelling, non-generic cover letters. Use the candidate's real achievements and tie them directly to the job description with storytelling."
    },
    "🧠 Interview Coach": {
        "emoji": "🎤",
        "system": "You are a STAR-method interview coach. Generate behavioral answers, prepare for technical questions, and simulate mock interviews."
    },
    "🔍 Job Researcher": {
        "emoji": "🔎",
        "system": "You analyze available jobs and suggest best matches and hidden opportunities."
    },
    "📈 Salary & Negotiation": {
        "emoji": "💰",
        "system": "You provide realistic salary benchmarks and negotiation scripts."
    },
    "🚀 Upskill Advisor": {
        "emoji": "📚",
        "system": "You analyze skill gaps and create personalized learning plans."
    }
}

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.warning("⚠️ Please enter your NVIDIA API Key in the sidebar.")
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=st.session_state.nvidia_api_key)

def call_nvidia_llm(messages, temperature=None, max_tokens=2048):
    client = get_nvidia_client()
    if not client:
        return "❌ Please provide a valid NVIDIA API key."
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("selected_model"),
            messages=messages,
            temperature=temperature or st.session_state.get("temperature", 0.7),
            max_tokens=max_tokens,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ NVIDIA API Error: {str(e)}"

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "📝 Profile"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2:
        location_filter = st.selectbox("■ Location", ["All Locations", "North Mankato"])
    with col3:
        job_type = st.selectbox("■ Type", ["All Types", "Part Time >19 hours a week"])
    with col4:
        min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)
    
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

# ==================== TAB 2: AI JOB ASSISTANT (with Agents) ====================
with tab2:
    st.markdown("### 💬 AI Job Assistant — Multi-Agent Studio")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select Specialist")
        selected_agent_name = st.selectbox("Agent", list(AGENTS.keys()), key="agent_select")
        agent = AGENTS[selected_agent_name]
        st.info(f"{agent['emoji']} **Active:** {selected_agent_name}")
        
        if st.button("Start New Conversation", type="primary"):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        st.subheader("Chat with Agent")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-msg"><strong>{selected_agent_name}:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

        # Chat input
        if prompt := st.chat_input("Describe the job or what you need help with..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.spinner(f"Thinking with {selected_agent_name}..."):
                context = {
                    "current_jobs": st.session_state.jobs.to_dict(orient="records"),
                    "candidate_profile": st.session_state.profile.iloc[0].to_dict(),
                    "candidate_extra": st.session_state.candidate_profile
                }
                
                full_prompt = f"""
                Context:
                {json.dumps(context, indent=2)}
                
                User request: {prompt}
                """
                
                messages = [
                    {"role": "system", "content": agent["system"]},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_nvidia_llm(messages, temperature=st.session_state.temperature)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            st.rerun()

    st.caption("Multi-agent system powered by NVIDIA NIM • Select different specialists above")

# ==================== TAB 3: PROFILE ====================
with tab3:
    st.markdown("### 📝 Profile")
    profile_form = st.form("profile_form")
    profile_form.subheader("Update Your Profile")
    
    name = profile_form.text_input("Name", value=st.session_state.profile['name'].iloc[0])
    location = profile_form.text_input("Location", value=st.session_state.profile['location'].iloc[0])
    experience = profile_form.text_area("Experience", value=st.session_state.profile['experience'].iloc[0])
    skills = profile_form.text_area("Skills", value=st.session_state.profile['skills'].iloc[0])
    education = profile_form.text_area("Education", value=st.session_state.profile['education'].iloc[0])
    certifications = profile_form.text_area("Certifications", value=st.session_state.profile['certifications'].iloc[0])
    
    submit_button = profile_form.form_submit_button("Save Profile")
    if submit_button:
        st.session_state.profile['name'] = name
        st.session_state.profile['location'] = location
        st.session_state.profile['experience'] = experience
        st.session_state.profile['skills'] = skills
        st.session_state.profile['education'] = education
        st.session_state.profile['certifications'] = certifications
        st.session_state.candidate_profile = {"name": name, "location": location}
        st.success("Profile saved!")
    
    st.download_button("Download Profile", data=st.session_state.profile.to_csv(index=False), file_name="profile.csv")

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant")
