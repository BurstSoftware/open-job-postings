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

    model_options = ["meta/llama-3.1-70b-instruct"]
    selected_model = st.selectbox("Select Model", model_options, index=0)
    st.session_state.selected_model = selected_model

    st.divider()
    page = st.radio("Navigate", 
                    ["📋 Job Listings", "💬 AI Job Assistant"],
                    label_visibility="collapsed")

    st.divider()
    st.info("Prototype with NVIDIA NIM • 50-State Search", icon="ℹ️")

# ====================== SESSION STATE INITIALIZATION ======================
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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "saved_search_filters" not in st.session_state:
    st.session_state.saved_search_filters = {
        "search": "",
        "location": "All Locations",
        "job_type": "All Types",
        "min_salary": 30000
    }

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

def extract_salary_value(s):
    """Normalize salary to approximate annual USD for filtering."""
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
        val *= 2080  # rough annual (40h/week * 52)
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

# 50 US States & Job Types
US_STATES = ["All Locations", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
             "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
             "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
             "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", 
             "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", 
             "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
             "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", 
             "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

JOB_TYPES = ["All Types", "Full Time", "Part Time", "Contract", "Remote"]

# ====================== PAGE ROUTING ======================
if page == "📋 Job Listings":
    st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
    st.markdown("### ■ Discover Your Next Role")

    # === NEW: Filter Controls ===
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
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """)
            col_a, _ = st.columns([1, 4])
            with col_a:
                if st.button("🚀 Apply Now", key=f"apply_{job['id']}"):
                    st.session_state.applications.append(job.to_dict())
                    st.success("✅ Application submitted!")

elif page == "💬 AI Job Assistant":
    st.markdown('<h1 class="header-title">Define Your Perfect Job</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Example prompts:**  
    • *Fire Fighter in Minneapolis, Full Time, around 75k*  
    • *Remote Software Engineer, Python, 150k+*  
    • *Registered Nurse in Minnesota, good benefits*
    """)
    
    st.divider()

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-msg"><strong>🤖 AI Job Assistant:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    # Chat input + AI Agent logic
    if prompt := st.chat_input("Describe your ideal job (e.g. Fire Fighter, Minneapolis, Full Time, 75k Salary...)"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("🔍 Parsing your request + searching across all job domains..."):
            # 1. Parse natural language into structured filters using LLM
            parse_prompt = f"""You are an expert job search query parser. 
Extract structured parameters from the user's description. 
Return ONLY a valid JSON object (no markdown, no extra text).

Keys:
- job_title: string (best title/keywords)
- location: string ("All Locations", city, state, or "Remote")
- job_type: "Full Time", "Part Time", "Contract", "Remote", or "All Types"
- min_salary: integer (approximate annual USD, e.g. 75000 for 75k)
- keywords: list of strings

User: {prompt}"""

            parsed_str = call_nvidia_llm(parse_prompt, temperature=0.2, max_tokens=400)
            
            try:
                cleaned = parsed_str.strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(cleaned)
            except:
                parsed = {
                    "job_title": prompt,
                    "location": "All Locations",
                    "job_type": "All Types",
                    "min_salary": 0,
                    "keywords": []
                }

            # 2. Update saved filters
            filters = st.session_state.saved_search_filters.copy()
            if parsed.get("location"):
                filters["location"] = parsed["location"]
            if parsed.get("job_type"):
                filters["job_type"] = parsed["job_type"]
            if parsed.get("min_salary", 0) > 0:
                filters["min_salary"] = parsed["min_salary"]
            if parsed.get("job_title"):
                filters["search"] = parsed["job_title"]

            st.session_state.saved_search_filters = filters

            # 3. Get matching jobs
            filtered_df = apply_filters_to_jobs(filters)
            top_jobs = filtered_df.head(5).to_dict(orient="records")
            context = json.dumps(top_jobs, indent=2) if top_jobs else "No strong matches found."

            # 4. Generate friendly recommendation
            assistant_prompt = f"""You are a friendly, expert AI Job Assistant.

User's request: "{prompt}"
Parsed filters: {json.dumps(parsed, indent=2)}

Matching jobs found:
{context}

Respond with:
- Brief confirmation of what you understood
- 3-5 best matching jobs (use the data above)
- Why each one is a good fit (salary, location, type, key reasons)
- Clear next steps
Keep it concise, encouraging, and actionable. Use bullet points."""

            response = call_nvidia_llm(assistant_prompt, temperature=0.75, max_tokens=1100)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # === Always show current matching jobs in AI page ===
    st.divider()
    st.subheader("📋 Jobs Matching Your Latest AI Search")

    current_df = apply_filters_to_jobs(st.session_state.saved_search_filters)
    st.caption(f"{len(current_df)} jobs found • Sorted by match score")

    if current_df.empty:
        st.info("No matches yet. Describe your ideal job in the chat above!")
    else:
        for _, job in current_df.iterrows():
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
                    <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply</a></div>
                    <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
                </div>
            </div>
            """)
            col_a, _ = st.columns([1, 4])
            with col_a:
                if st.button("🚀 Apply Now", key=f"ai_apply_{job['id']}"):
                    st.session_state.applications.append(job.to_dict())
                    st.success("✅ Application submitted!")

    # Quick reset button
    if st.button("🔄 Reset Search (Show All Jobs)", use_container_width=True):
        st.session_state.saved_search_filters = {
            "search": "",
            "location": "All Locations",
            "job_type": "All Types",
            "min_salary": 30000
        }
        st.rerun()

# Footer
st.markdown("---")
st.caption("Open Job Postings • Powered by NVIDIA NIM • 50-State AI Search")
