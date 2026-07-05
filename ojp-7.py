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
.chat-message { padding: 12px 16px; border-radius: 12px; margin: 8px 0; }
.user-msg { background: #2a3b6e; margin-left: 20%; }
.ai-msg { background: #1e2a5c; margin-right: 20%; }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()

    st.subheader("🔑 NVIDIA NIM Settings")
    
    api_key = st.text_input(
        "NVIDIA API Key (nvapi-...)", 
        type="password",
        value=st.session_state.get("nvidia_api_key", ""),
        help="Paste your key from https://build.nvidia.com/. It will be saved for this session."
    )
    
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()

    model_options = [
        "meta/llama-3.1-70b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "meta/llama-3.1-8b-instruct",
        "mistralai/mistral-nemo"
    ]
    selected_model = st.selectbox("Select Model", model_options, index=0)
    st.session_state.selected_model = selected_model

    st.divider()
    page = st.radio("Navigate", 
                    ["📋 Job Listings", "🔍 AI Job Finder", "💬 AI Job Assistant"],
                    label_visibility="collapsed")

    st.divider()
    if st.button("Clear All Data (Dev)", use_container_width=True):
        if "jobs" in st.session_state:
            del st.session_state.jobs
        if "chat_history" in st.session_state:
            del st.session_state.chat_history
        if "applications" in st.session_state:
            del st.session_state.applications
        st.rerun()
    
    st.info("Prototype with NVIDIA NIM", icon="ℹ️")

# ====================== SESSION STATE INITIALIZATION ======================
if "jobs" not in st.session_state:
    jobs_list = [{
        "id": str(uuid.uuid4()),
        "title": "DemoJob.Job1",
        "company": "ABC Test Company 1",
        "location": "Minneapolis, MN 55401",
        "salary": "$75/hr",
        "posted": "2026-07-04",
        "type": "Full Time",
        "match": 92,
        "website": "https://abc.com",
        "phone": "555-123-4567",
        "description": "test",
        "requirements": "test",
        "benefits": "test",
        "referrer": "demo"
    }]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.warning("⚠️ Please enter your NVIDIA API Key in the sidebar.")
        return None
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=st.session_state.nvidia_api_key
    )

def call_nvidia_llm(prompt, temperature=0.7, max_tokens=1024):
    client = get_nvidia_client()
    if not client:
        return "❌ Please provide a valid NVIDIA API key in the sidebar."
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("selected_model", "meta/llama-3.1-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ NVIDIA API Error: {str(e)}"

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

# ====================== PAGE ROUTING ======================
if page == "📋 Job Listings":
    st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
    st.markdown("### ■ Discover Your Next Role")

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search = st.text_input("■ Search titles, skills, companies...", placeholder="Amazon Flex, warehouse")
    with col2:
        location_filter = st.selectbox("■ Location", ["All Locations", "Minneapolis"])
    with col3:
        job_type = st.selectbox("■ Type", ["All Types", "Full Time"])
    with col4:
        min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)

    # Filtering
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

    st.caption(f"Showing **{len(df)}** high-quality opportunities")

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
                
                <div style="margin:18px 0 16px 0;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <span class="badge">Match: {job.get('match', 85)}%</span>
                </div>

                <div class="info-label">Description</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('description','')}</div>
                
                <div class="info-label">Requirements</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('requirements','')}</div>
                
                <div class="info-label">Benefits</div>
                <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">{job.get('benefits','')}</div>
                
                <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">{job.get('website','abc.com')}</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """)
            col_a, _ = st.columns([1, 4])
            with col_a:
                st.link_button("🚀 Apply Now", url=job.get("website", "#"), use_container_width=True)

elif page == "🔍 AI Job Finder":
    st.markdown('<h1 class="header-title">AI Job Finder</h1>', unsafe_allow_html=True)
    st.markdown("### 🚀 Powered by NVIDIA NIM")

    # Aligned input + button
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Describe the jobs you're looking for...", 
                             "warehouse jobs at WMN7 in North Mankato, MN",
                             label_visibility="collapsed")
    with col2:
        if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
            if query:
                with st.spinner("Querying NVIDIA LLM..."):
                    prompt = f"""Return 3-5 plausible job postings as JSON array for this query: "{query}".
                    Each object must have: title, company, location, salary, type, description, requirements, benefits."""
                    result = call_nvidia_llm(prompt, temperature=0.6)
                    try:
                        new_jobs = json.loads(result)
                        if isinstance(new_jobs, list):
                            new_df = pd.DataFrame(new_jobs)
                            for col in ["id","posted","match","website","phone","referrer"]:
                                if col not in new_df.columns: 
                                    new_df[col] = [""] * len(new_df)
                            st.session_state.jobs = pd.concat([st.session_state.jobs, new_df], ignore_index=True)
                            st.success(f"Added {len(new_df)} new jobs!")
                            st.rerun()
                    except:
                        st.info("LLM Response (raw):")
                        st.code(result)

    st.markdown("### Current Job Listings")
    st.dataframe(st.session_state.jobs, use_container_width=True)

elif page == "💬 AI Job Assistant":
    st.markdown('<h1 class="header-title">AI Job Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### 💬 Chat with NVIDIA NIM")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-msg"><strong>AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask anything about jobs, applications, or career advice..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Thinking with NVIDIA NIM..."):
            context = str(st.session_state.jobs.head(8).to_dict(orient="records"))
            full_prompt = f"""You are a helpful AI career assistant.
Context (recent jobs): {context}

User Question: {prompt}
Answer helpfully and concisely."""
            response = call_nvidia_llm(full_prompt, temperature=0.7)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

st.markdown("---")
st.caption("Open Job Postings")
