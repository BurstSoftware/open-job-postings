import streamlit as st
import pandas as pd
import uuid
import re
import json
import time

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ `openai` package is not installed. Run: `pip install openai`")
    st.stop()

# ====================== CONFIG & CSS ======================
st.set_page_config(
    page_title="NVIDIA NIM Career Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
.job-card { background: linear-gradient(145deg, #16213e, #1e2a5c); border-radius: 20px; padding: 24px; margin: 16px 0; 
            border: 1px solid #4a5d9e; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.job-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(74,93,158,0.4); border-color: #6e8cff; }
.job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
.company { color: #8f9eff; font-weight: 600; }
.badge { display: inline-block; background: #3a4a8c; color: #c0d0ff; padding: 4px 12px; border-radius: 30px; 
         font-size: 0.8rem; margin-right: 8px; }
.info-label { font-weight: 600; color: #8899cc; margin-top: 16px; margin-bottom: 6px; font-size: 0.95rem; }
.header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "meta/llama-3.1-70b-instruct"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

if "jobs" not in st.session_state:
    jobs_list = [
        {
            "id": str(uuid.uuid4()),
            "title": "Amazon Flex - X / L1",
            "company": "Amazon",
            "location": "North Mankato, MN",
            "salary": "$19/hr",
            "posted": "2026-07-04",
            "type": "Part Time",
            "match": 78,
            "website": "https://www.amazon.com/getpaid",
            "phone": "N/A",
            "description": "Picking, Packing, Sorting, Stowing in a fast-paced warehouse environment.",
            "requirements": "Lifting up to 49lbs, twisting, bending, stooping. Must have reliable transportation.",
            "benefits": "Flexible hours, benefits through A to Z app, weekly pay.",
            "referrer": "narossoh"
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "saved_search_filters" not in st.session_state:
    st.session_state.saved_search_filters = {
        "search": "",
        "location": "All Locations",
        "job_type": "All Types",
        "min_salary": 30000
    }

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== DEFAULT AGENTS ======================
DEFAULT_AGENTS = {
    "📄 Resume Optimizer": {
        "role": "ATS Strategist & Resume Expert", 
        "goal": "Align resumes with job descriptions to clear ATS filters and highlight high-impact metrics.",
        "backstory": "You are a seasoned technical recruiter who knows exactly how applicant tracking systems screen resumes and what hiring managers look for in the first 6 seconds.",
        "system_prompt": "You are an expert resume writer and ATS optimizer. Help the user tailor their experience to a specific job description. Identify missing keywords, rephrase impact statements using the Google X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]), and suggest structural improvements."
    },
    "✉️ Cover Letter Specialist": {
        "role": "Executive Copywriter", 
        "goal": "Craft compelling, narrative-driven cover letters that connect personal background to company mission.",
        "backstory": "You are a professional writer who specializes in career storytelling, helping candidates bridge their skills with a company's specific problems and goals.",
        "system_prompt": "You are a professional cover letter writer. Draft engaging, highly tailored cover letters that hook the reader immediately. Align the candidate's achievements with the company's culture and current initiatives. Avoid generic clichés like 'I am writing to express my interest'—instead, start with a powerful hook."
    },
    "🎯 Interview Coach": {
        "role": "Mock Interviewer & Performance Coach", 
        "goal": "Prepare candidates for behavioral, situational, and technical interview questions.",
        "backstory": "You are an encouraging yet challenging career coach who has conducted thousands of hiring loops across tech and corporate industries.",
        "system_prompt": "You are an expert interview coach. Conduct a realistic mock interview. Ask exactly ONE question at a time (mixing behavioral and technical/situational questions relevant to the user's target role). Wait for the user to respond, then provide constructive feedback on their answer structure (using the STAR method) before moving on to the next question."
    },
    "🔍 Market & Company Scout": {
        "role": "Job Market Intelligence Analyst", 
        "goal": "Analyze target companies, decode job descriptions, and extract hidden organizational requirements.",
        "backstory": "You are a corporate intelligence analyst who reverse-engineers vague job descriptions to discover the exact core problems a team is hiring to solve.",
        "system_prompt": "You are a job market scout. Analyze job descriptions or company details provided by the user. Break down the unstated tech/skills required, identify potential internal team pain points, and provide high-value talking points or questions the user can ask to stand out."
    },
    "💰 Offer Negotiator": {
        "role": "Compensation Consultant", 
        "goal": "Maximize total compensation packages and confidently navigate complex salary and equity discussions.",
        "backstory": "You are a former corporate Talent Acquisition Director who knows internal compensation brackets, sign-on bonus allocation rules, and equity vesting cycles.",
        "system_prompt": "You are an expert compensation negotiator. Advise the user on handling initial compensation expectations, scripting counter-offers, and maximizing total compensation (base, bonus, equity, benefits). Provide tactical, script-ready lines the user can copy and paste into emails or use over the phone."
    }
}

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your NVIDIA API Key in the sidebar.")
        return None
    try:
        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=st.session_state.api_key
        )
    except Exception as e:
        st.error(f"Client Error: {e}")
        return None

def generate_response(prompt, agent=None):
    client = get_nvidia_client()
    if not client:
        return None
    
    messages = []
    if agent and agent.get("system_prompt"):
        messages.append({"role": "system", "content": agent["system_prompt"]})
    
    # Include history for continuity
    for msg in st.session_state.current_chat:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
            temperature=st.session_state.temperature,
            max_tokens=4096,
            stream=True
        )
        return response
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def extract_salary_value(s):
    s = str(s).lower().replace('$', '').replace(',', '').strip()
    match = re.search(r'(\d+(?:\.\d+)?)\s*(k|hr|hour| /hr)?', s)
    if not match:
        nums = re.findall(r'\d+', s)
        return int(nums[0]) if nums else 0
    val = float(match.group(1))
    unit = match.group(2) or ''
    if 'k' in unit:
        val *= 1000
    elif 'hr' in unit or 'hour' in unit:
        val *= 2080
    return int(val)

def apply_filters_to_jobs(filters):
    df = st.session_state.jobs.copy()
    if filters["search"]:
        df = df[
            df['title'].str.contains(filters["search"], case=False, na=False) | 
            df['company'].str.contains(filters["search"], case=False, na=False) |
            df['description'].str.contains(filters["search"], case=False, na=False)
        ]
    if filters["location"] != "All Locations":
        df = df[df['location'].str.contains(filters["location"], case=False, na=False)]
    if filters["job_type"] != "All Types":
        df = df[df['type'].str.contains(filters["job_type"], case=False, na=False)]
    
    df = df[df['salary'].apply(extract_salary_value) >= filters["min_salary"]]
    df = df.sort_values(by="match", ascending=False)
    return df

US_STATES = ["All Locations", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
             "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
             "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
             "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", 
             "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", 
             "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
             "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", 
             "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

JOB_TYPES = ["All Types", "Full Time", "Part Time", "Contract", "Remote"]

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Job Studio**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()

    page = st.radio("Navigate", ["📋 Job Listings", "💼 AI Career Agents"], label_visibility="collapsed")
    st.divider()

    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input(
        "NVIDIA API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your free key → https://build.nvidia.com/",
        placeholder="nvapi-..."
    )
    if api_key:
        st.session_state.api_key = api_key

    nvidia_models = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3",
        "qwen/qwen2.5-72b-instruct",
        "mistralai/mistral-large",
        "google/gemma-2-27b-it",
    ]
    st.session_state.model_name = st.selectbox("NVIDIA Model", nvidia_models, index=0)
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)

    if page == "💼 AI Career Agents":
        st.divider()
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.current_chat = []
            st.rerun()

    st.divider()
    st.caption("Prototype with NVIDIA NIM • 50-State Search")

# ====================== MAIN ROUTING ======================
if page == "📋 Job Listings":
    st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
    st.markdown("### ■ Discover Your Next Role")

    filters = st.session_state.saved_search_filters
    with st.expander("🔍 Refine Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("Search keywords", value=filters["search"])
        with col2:
            loc_index = US_STATES.index(filters["location"]) if filters["location"] in US_STATES else 0
            location = st.selectbox("Location", US_STATES, index=loc_index)
        with col3:
            type_index = JOB_TYPES.index(filters["job_type"]) if filters["job_type"] in JOB_TYPES else 0
            job_type = st.selectbox("Job Type", JOB_TYPES, index=type_index)
        
        min_sal = st.slider("Minimum Annual Salary ($)", 0, 300000, filters["min_salary"], step=5000)
        
        if st.button("Apply Filters", use_container_width=True):
            st.session_state.saved_search_filters = {
                "search": search,
                "location": location,
                "job_type": job_type,
                "min_salary": min_sal
            }
            st.rerun()

    df = apply_filters_to_jobs(st.session_state.saved_search_filters)
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
                        <div style="font-size:1.2rem; font-weight:700; color:#00ff9d;">{job['salary']}</div>
                        <div style="color:#8899cc;">{job['location']}</div>
                    </div>
                </div>
                <div style="margin:18px 0 16px 0;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <div style="margin-top: 10px;">
                        <span class="badge">Match: {job.get('match', 80)}%</span>
                    </div>
                </div>
                <div class="info-label">Description</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('description','')}</div>
                <div class="info-label">Requirements</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('requirements','')}</div>
                <div class="info-label">Benefits</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">{job.get('benefits','')}</div>
                <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply Link</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Apply Button directly underneath the HTML block
            col_a, _ = st.columns([1, 4])
            with col_a:
                if st.button("🚀 Apply Now", key=f"apply_{job['id']}"):
                    st.session_state.applications.append(job.to_dict())
                    st.success("✅ Application submitted!")

elif page == "💼 AI Career Agents":
    st.markdown('<h1 class="header-title">AI Career Assistant Studio</h1>', unsafe_allow_html=True)
    
    # Agent Selection
    agent_names = list(DEFAULT_AGENTS.keys())
    selected_agent_name = st.selectbox("Select Career Assistant Agent", agent_names, index=0)
    st.session_state.selected_agent = DEFAULT_AGENTS[selected_agent_name]

    with st.expander(f"ℹ️ Agent Dossier: {selected_agent_name}", expanded=True):
        st.markdown(f"**Role:** {st.session_state.selected_agent['role']}")
        st.markdown(f"**Objective:** {st.session_state.selected_agent['goal']}")
        st.markdown(f"**Backstory:** *{st.session_state.selected_agent['backstory']}*")

    st.divider()

    # Chat Interface
    for msg in st.session_state.current_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Paste a job description, paste your resume, or ask a question..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response = generate_response(prompt, st.session_state.selected_agent)
            
            if response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                # Append to history AFTER generation finishes
                st.session_state.current_chat.append({"role": "user", "content": prompt})
                st.session_state.current_chat.append({"role": "assistant", "content": full_response})
            else:
                st.warning("Could not get a response. Please check your API key and network connection.")
