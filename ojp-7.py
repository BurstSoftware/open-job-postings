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
.match-bar { height: 6px; background: linear-gradient(90deg, #00ff9d, #6e8cff); border-radius: 10px; }
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
    ]
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
            "match": 92,
            "website": "http://amazon.com/getpaid",
            "phone": "N/A",
            "description": "Picking, Packing, Sorting, Stowing in a fast-paced warehouse environment.",
            "requirements": "Lifting up to 49lbs, twisting, bending, stooping. Must have reliable transportation.",
            "benefits": "Flexible hours, benefits through A to Z app, weekly pay.",
            "referrer": "narossoh"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Warehouse Associate",
            "company": "Target",
            "location": "Austin, TX",
            "salary": "$18/hr",
            "posted": "2026-07-03",
            "type": "Full Time",
            "match": 88,
            "website": "#",
            "phone": "N/A",
            "description": "Order fulfillment, inventory management, and shipping.",
            "requirements": "Previous warehouse experience preferred.",
            "benefits": "Health insurance, 401k, employee discount.",
            "referrer": "targetcareers"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Delivery Driver",
            "company": "DoorDash",
            "location": "Los Angeles, CA",
            "salary": "$20-28/hr",
            "posted": "2026-07-02",
            "type": "Part Time",
            "match": 95,
            "website": "#",
            "phone": "N/A",
            "description": "Flexible delivery gigs using your own vehicle.",
            "requirements": "Valid driver's license, insured vehicle.",
            "benefits": "Instant cashout, flexible schedule.",
            "referrer": "doordash"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Software Engineer - Backend",
            "company": "Stripe",
            "location": "New York, NY",
            "salary": "$140k-180k",
            "posted": "2026-07-01",
            "type": "Full Time",
            "match": 78,
            "website": "#",
            "phone": "N/A",
            "description": "Build scalable payment infrastructure.",
            "requirements": "Python, Go, or Java experience.",
            "benefits": "Equity, unlimited PTO, top-tier health.",
            "referrer": "stripe"
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
        "min_salary": 15
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

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

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
    
    df = df[df['salary'].apply(extract_min_salary) >= filters["min_salary"]]
    # Sort by match score (higher is better)
    df = df.sort_values(by="match", ascending=False)
    return df

# 50 US States
US_STATES = [
    "All Locations", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", 
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", 
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", 
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

JOB_TYPES = ["All Types", "Full Time", "Part Time", "Contract", "Remote"]

# ====================== PAGE ROUTING ======================
if page == "📋 Job Listings":
    st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
    st.markdown("### ■ Discover Your Next Role")
    
    df = apply_filters_to_jobs(st.session_state.saved_search_filters)
    st.caption(f"Showing **{len(df)}** opportunities")

    if df.empty:
        st.warning("No jobs match your saved filters.")
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
                        <span class="badge">Match: {job.get('match', 85)}%</span>
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
    st.markdown('<h1 class="header-title">AI Job Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### 💬 Chat with NVIDIA NIM • Smart 50-State Job Search")

    # ====================== ENHANCED SEARCH FILTERS ======================
    st.subheader("🔍 Define Your Perfect Job")
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
    
    with col1:
        search = st.text_input("■ Job Title / Skills / Company", 
                              value=st.session_state.saved_search_filters["search"],
                              placeholder="Warehouse, driver, software engineer...")
    with col2:
        location_filter = st.selectbox("■ State", 
                                      US_STATES,
                                      index=US_STATES.index(st.session_state.saved_search_filters["location"]))
    with col3:
        job_type = st.selectbox("■ Job Type", 
                               JOB_TYPES,
                               index=JOB_TYPES.index(st.session_state.saved_search_filters["job_type"]))
    with col4:
        min_salary = st.slider("■ Min Hourly ($)", 0, 300, 
                              value=st.session_state.saved_search_filters["min_salary"])
    with col5:
        st.write("")  # Spacer

    if st.button("💾 Save & Search", type="primary", use_container_width=True):
        st.session_state.saved_search_filters = {
            "search": search,
            "location": location_filter,
            "job_type": job_type,
            "min_salary": min_salary
        }
        st.success("✅ Filters saved! Chat below to get personalized recommendations.", icon="🔄")
        st.rerun()

    st.divider()

    # ====================== CHAT INTERFACE ======================
    st.subheader("💬 Ask Anything")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-msg"><strong>🤖 AI Assistant:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Example: Show me warehouse jobs in Texas paying over $18/hr..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("🔍 Searching 50 states + analyzing best matches..."):
            filters = st.session_state.saved_search_filters
            filtered_jobs = apply_filters_to_jobs(filters)
            
            # Limit to top 5 for context
            top_jobs = filtered_jobs.head(5)
            context = str(top_jobs.to_dict(orient="records"))
            
            full_prompt = f"""You are an expert career coach using real-time job data.

Current filters: {filters}
Found {len(filtered_jobs)} matching jobs.

Top jobs (use these to make recommendations):
{context}

User request: {prompt}

Rules:
- Be friendly, concise, and actionable.
- Always recommend 3-5 specific jobs from the list above when possible.
- Highlight why each job matches the user.
- Include salary, location, and a direct call-to-action.
- If no jobs match, suggest broadening filters."""

            response = call_nvidia_llm(full_prompt, temperature=0.75)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# Footer
st.markdown("---")
st.caption("Open Job Postings • Powered by NVIDIA NIM • 50-State AI Search")
