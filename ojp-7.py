import streamlit as st
import pandas as pd
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
        padding: 28px; 
        margin: 20px 0; 
        border: 1px solid #4a5d9e; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.4); 
    }
    .job-title { font-size: 1.75rem; font-weight: 700; color: #a0c4ff; margin-bottom: 6px; }
    .salary { font-size: 1.65rem; font-weight: 700; color: #00ff9d; }
    .company { color: #8f9eff; font-weight: 600; font-size: 1.1rem; }
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
    .header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    
    .apply-btn {
        background: linear-gradient(90deg, #00ff9d, #00e68a);
        color: #0f0f23;
        font-weight: 700;
        padding: 16px 50px;
        border-radius: 50px;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 20px;
        display: block;
        text-decoration: none;
        box-shadow: 0 8px 25px rgba(0, 255, 157, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("For support, [burstsoftwaredevelopment@gmail.com](mailto:burstsoftwaredevelopment@gmail.com)")
    st.info("Powered by NVIDIA NIM", icon="ℹ️")

# ====================== INITIAL DATA ======================
if "jobs" not in st.session_state:
    jobs_list = [
        {
            "id": str(uuid.uuid4()),
            "title": "Amazon Flex - X",
            "company": "Amazon - WMN7",
            "location": "North Mankato, MN 56003",
            "salary": "$19/hr",
            "posted": "2026-07-04",
            "type": "Part Time >19 hours a week",
            "match": 92,
            "website": "http://amazon.com/getpaid",
            "phone": "555-123-4567",
            "description": "picking, packing, stowing, water spider",
            "requirements": "lifting up to 49lbs, twisting, bending, stooping, picking, packing",
            "benefits": "benefits available through the A to Z app",
            "referrer": "narossoh"
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== AGENTS ======================
AGENTS = {
    "🎯 Job Match Analyst": {
        "emoji": "📊",
        "description": "Analyzes how well a job matches your profile and gives fit scores.",
        "system": "You are an expert job-market analyst. Score job fit (0-100), highlight matches, red flags, and suggest improvements."
    },
    "📝 CV Tailor": {
        "emoji": "📄",
        "description": "Expert CV writer that tailors your resume to specific job descriptions.",
        "system": "You are a world-class CV writer. Optimize for ATS and use strong action verbs."
    },
    "✉️ Cover Letter Writer": {
        "emoji": "💌",
        "description": "Creates personalized, compelling cover letters.",
        "system": "You write compelling, non-generic cover letters tied directly to the job."
    },
    "🧠 Interview Coach": {
        "emoji": "🎤",
        "description": "Prepares you for interviews with STAR method answers.",
        "system": "You are a STAR-method interview coach. Generate behavioral answers."
    }
}

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    try:
        key = st.secrets.get("NVIDIA_API_KEY") or st.secrets.get("nvidia", {}).get("api_key")
        if not key:
            st.warning("⚠️ NVIDIA API Key is missing.")
            return None
        return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key)
    except Exception:
        st.warning("⚠️ NVIDIA API Key is missing.")
        return None

def call_nvidia_llm(messages):
    client = get_nvidia_client()
    if not client:
        return "❌ Please provide a valid NVIDIA API key in Streamlit Secrets."
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=messages,
            temperature=0.7,
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

tab1, tab2, tab3 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "🚀 Submit a Job"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
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
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="job-title">{job['title']}</div>
                        <div class="company">■ {job['company']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="salary">{job['salary']}</div>
                        <div style="color:#8899cc; margin-top: 6px;">{job['location']}</div>
                    </div>
                </div>
                
                <div style="margin: 24px 0 20px 0; display: flex; flex-wrap: wrap; gap: 10px;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <span class="badge">Match: {job.get('match', 85)}%</span>
                </div>
                
                <div style="margin-bottom: 18px;">
                    <strong>Description</strong><br>
                    {job.get('description','')}
                </div>
                <div style="margin-bottom: 18px;">
                    <strong>Requirements</strong><br>
                    {job.get('requirements','')}
                </div>
                <div style="margin-bottom: 22px;">
                    <strong>Benefits</strong><br>
                    {job.get('benefits','')}
                </div>
                
                <div style="border-top: 1px solid #334477; padding-top: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div>
                        <strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">amazon.com/getpaid</a><br>
                        <strong>Phone:</strong> {job.get('phone','N/A')}
                    </div>
                    <div>
                        <a href="{job.get('website','#')}" target="_blank" class="apply-btn">🚀 Apply Now</a>
                    </div>
                </div>
                
                <div style="margin-top: 16px; color:#8899cc; font-size: 0.95rem;">
                    Referred By: {job.get('referrer','N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 2: AI JOB ASSISTANT ====================
with tab2:
    st.markdown("### 💬 AI Job Assistant — Multi-Agent Studio")
    selected_agent_name = st.selectbox("Select Specialist", list(AGENTS.keys()), key="agent_select")
    agent = AGENTS[selected_agent_name]
    
    if st.button("🗑️ New Conversation"):
        st.session_state.chat_history = []
        st.rerun()
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**{selected_agent_name}:** {msg['content']}")
    
    if prompt := st.chat_input("Describe the job or what you need help with..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            context = {"current_jobs": st.session_state.jobs.to_dict(orient="records")}
            messages = [
                {"role": "system", "content": agent["system"]},
                {"role": "user", "content": f"Context: {json.dumps(context)}\n\nRequest: {prompt}"}
            ]
            response = call_nvidia_llm(messages)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ==================== TAB 3: SUBMIT JOB ====================
with tab3:
    st.markdown("### 🚀 Submit a Job Posting")
    
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: linear-gradient(145deg, #16213e, #1e2a5c); 
                border-radius: 20px; border: 2px solid #00ff9d; margin-bottom: 30px;">
        <h2 style="color: #00ff9d;">Get Your Job Live in 24 Hours</h2>
        <p style="font-size: 1.3rem; color: #e0e0ff;">
            Submit your job once.<br>
            We manually review it and make it live <strong>within 24 hours</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        label="📋 Fill Out the Form & List Your Job Now — Only $49/month",
        url="https://forms.gle/Yjzx9cbrMWZ6mrA58",
        use_container_width=True
    )

    st.markdown("### How It Works")
    col1, col2, col3 = st.columns(3)
    with col1: st.info("**1. Fill the Form**")
    with col2: st.info("**2. We Review** (Manual check)")
    with col3: st.info("**3. Go Live** (Within 24 hours)")

    st.success("💡 All submissions are reviewed for quality before going live.")

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant • Employers: $49/month listings")
