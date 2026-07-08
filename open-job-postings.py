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

# ====================== AGENTS ======================
AGENTS = {
    "🎯 Job Match Analyst": {
        "emoji": "📊",
        "description": "Analyzes how well a job matches your profile and gives fit scores with improvement tips.",
        "system": "You are an expert job-market analyst. Score job fit (0-100), highlight must-have vs nice-to-have matches, red flags, and suggest exact tailoring strategies."
    },
    "📝 CV Tailor": {
        "emoji": "📄",
        "description": "Expert CV writer that tailors your resume to specific job descriptions and optimizes for ATS.",
        "system": "You are a world-class CV writer. Convert achievements into strong bullet points using action verbs. Optimize for ATS."
    },
    "✉️ Cover Letter Writer": {
        "emoji": "💌",
        "description": "Creates personalized, compelling cover letters that stand out to recruiters.",
        "system": "You write compelling, non-generic cover letters tied directly to the job description."
    },
    "🧠 Interview Coach": {
        "emoji": "🎤",
        "description": "Prepares you for interviews with STAR method answers and mock interview practice.",
        "system": "You are a STAR-method interview coach. Generate behavioral answers and simulate mock interviews."
    },
    "📈 Salary & Negotiation": {
        "emoji": "💰",
        "description": "Provides salary benchmarks and negotiation strategies tailored to your experience.",
        "system": "You provide realistic salary benchmarks and negotiation scripts."
    },
    "🚀 Upskill Advisor": {
        "emoji": "📚",
        "description": "Identifies skill gaps and creates personalized learning plans to help you grow.",
        "system": "You analyze skill gaps and create personalized learning plans."
    }
}

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("■ Open Job Postings")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("For support: [burstsoftwaredevelopment@gmail.com](mailto:burstsoftwaredevelopment@gmail.com)")
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
            "phone": "N/A",
            "description": "picking, packing, stowing, water spider",
            "requirements": "lifting up to 49lbs, twisting, bending, stooping, picking, packing",
            "benefits": "benefits available through the A to Z app",
            "referrer": "narossoh"
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
st.title("Open Job Postings")

tab1, tab2, tab3 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "🚀 Submit a Job"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    st.subheader("Discover Your Next Role")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search = st.text_input("Search", placeholder="Amazon Flex, warehouse", label_visibility="collapsed")
    with col2:
        location_filter = st.selectbox("Location", ["All Locations", "North Mankato"], label_visibility="collapsed")
    with col3:
        job_type = st.selectbox("Type", ["All Types", "Part Time >19 hours a week"], label_visibility="collapsed")
    with col4:
        min_salary = st.slider("Min Hourly ($)", 0, 200, 15, label_visibility="collapsed")
    
    df = st.session_state.jobs.copy()
    
    if search:
        df = df[
            df['title'].str.contains(search, case=False, na=False) |
            df['company'].str.contains(search, case=False, na=False) |
            df['description'].str.contains(search, case=False, na=False)
        ]
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
            # Open the Amazon job by default
            is_amazon = "Amazon" in job['title']
            with st.expander(f"**{job['title']}** — {job['company']} • {job['salary']}", expanded=is_amazon):
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Type:** {job['type']}")
                    st.write(f"**Posted:** {job['posted']}")
                    st.write(f"**Match:** {job.get('match', 85)}%")
                with col_b:
                    st.write(f"**Website:** [Apply Here]({job.get('website', '#')})")
                    st.write(f"**Phone:** {job.get('phone', 'N/A')}")
                
                st.write("**Description**")
                st.write(job.get('description', ''))
                
                st.write("**Requirements**")
                st.write(job.get('requirements', ''))
                
                st.write("**Benefits**")
                st.write(job.get('benefits', ''))
                
                st.write(f"**Referred By:** {job.get('referrer', 'N/A')}")

# ==================== TAB 2: AI JOB ASSISTANT ====================
with tab2:
    st.subheader("AI Job Assistant — Multi-Agent Studio")
    
    selected_agent_name = st.selectbox(
        "Select Specialist", 
        list(AGENTS.keys())
    )
    agent = AGENTS[selected_agent_name]
    
    st.caption(f"{agent['emoji']} {agent['description']}")
    
    if st.button("🗑️ New Conversation"):
        st.session_state.chat_history = []
        st.rerun()
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant", avatar=agent['emoji']).write(msg["content"])
    
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
    st.subheader("Submit a Job Posting")
    
    st.info("""
    **Get Your Job Live in 24 Hours**
    
    Submit your job once. We manually review it and make it live within 24 hours.
    """)
    
    st.link_button(
        label="📋 Fill Out the Form & List Your Job Now — Only $49/month",
        url="https://forms.gle/Yjzx9cbrMWZ6mrA58",
        use_container_width=True
    )
    
    st.subheader("How It Works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**1. Fill the Form**")
    with col2:
        st.info("**2. We Review** (Manual check)")
    with col3:
        st.info("**3. Go Live** (Within 24 hours)")
    
    st.success("All submissions are reviewed for quality before going live.")

st.caption("Open Job Postings • NVIDIA NIM + Multi-Agent AI Assistant • Employers: $49/month listings")
