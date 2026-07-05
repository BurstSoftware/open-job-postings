# Updated Streamlit App with NVIDIA NIM Integration
# Copy and paste this entire code into your app.py file

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import io
from openai import OpenAI
import json

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (unchanged + minor additions) ======================
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    color: #e0e0ff;
}
.job-card {
    background: linear-gradient(145deg, #16213e, #1e2a5c);
    border-radius: 20px;
    padding: 24px;
    margin: 16px 0;
    border: 1px solid #4a5d9e;
    transition: all 0.3s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}
.job-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(74, 93, 158, 0.4);
    border-color: #6e8cff;
}
.job-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #a0c4ff;
    margin-bottom: 8px;
}
.company {
    color: #8f9eff;
    font-weight: 600;
}
.badge {
    display: inline-block;
    background: #3a4a8c;
    color: #c0d0ff;
    padding: 4px 12px;
    border-radius: 30px;
    font-size: 0.8rem;
    margin-right: 8px;
}
.info-label {
    font-weight: 600;
    color: #8899cc;
    margin-top: 16px;
    margin-bottom: 6px;
    font-size: 0.95rem;
}
.stButton>button {
    border-radius: 50px;
    height: 48px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 25px rgba(110, 140, 255, 0.4);
}
.header-title {
    font-size: 2.8rem;
    background: linear-gradient(90deg, #a0c4ff, #c0d0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.chat-message {
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
}
.user-msg {
    background: #2a3b6e;
    margin-left: 20%;
}
.ai-msg {
    background: #1e2a5c;
    margin-right: 20%;
}
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR - NVIDIA API CONFIG ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()

    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input(
        "NVIDIA API Key (nvapi-...)",
        type="password",
        value=st.session_state.get("nvidia_api_key", ""),
        help="Get free key at https://build.nvidia.com/"
    )
    if api_key:
        st.session_state.nvidia_api_key = api_key

    model_options = [
        "meta/llama-3.1-70b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "meta/llama-3.1-8b-instruct",
        "mistralai/mistral-nemo",
        # Add more from build.nvidia.com as needed
    ]
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=0
    )
    st.session_state.selected_model = selected_model

    st.divider()
    if st.button("Clear All Data (Dev)", use_container_width=True):
        if "jobs" in st.session_state:
            st.session_state.jobs = pd.DataFrame(jobs_list)
        st.session_state.applications = []
        st.rerun()
    st.markdown("---")
    st.info("Prototype • Built with ❤️ + NVIDIA NIM for Hackathon", icon="ℹ️")

# ====================== LOAD INITIAL DATA ======================
csv_data = """Timestamp,Business Name,Job Title,City,State,Zip Code,Job Type,Hourly Rate,Monthly Rate,Website,Phone,Job Description,Requirements,Benefits
2026-07-04 20:06:12,ABC Test Company 1,DemoJob.Job1,Minneapolis,MN,55401,Full Time,75.0,,abc.com,555-123-4567,test,test,test"""

df_raw = pd.read_csv(io.StringIO(csv_data))

jobs_list = []
for _, row in df_raw.iterrows():
    location = f"{row['City']}, {row['State']} {row['Zip Code']}"
    salary = f"${float(row['Hourly Rate']):.0f}/hr" if pd.notna(row['Hourly Rate']) else "Salary not listed"
    
    jobs_list.append({
        "id": str(uuid.uuid4()),
        "title": "Amazon Flex - X",
        "company": "Amazon",
        "location": "North Mankato, MN 56003",
        "salary": "$19/hr",
        "posted": row['Timestamp'].split()[0],
        "type": "Part Time >19 hours a week",
        "match": 92,
        "website": "http://amazon.com/getpaid",
        "phone": row.get('Phone', ''),
        "description": "picking, packing, stowing, water spider",
        "requirements": "lifting up to 49lbs, twisting, bending, stooping, picking, packing",
        "benefits": "benefits available through the A to Z app",
        "referrer": "narossoh"
    })

if "jobs" not in st.session_state:
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "applications" not in st.session_state:
    st.session_state.applications = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.error("Please enter your NVIDIA API Key in the sidebar.")
        return None
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=st.session_state.nvidia_api_key
    )

def call_nvidia_llm(prompt, temperature=0.7, max_tokens=1024):
    client = get_nvidia_client()
    if not client:
        return "❌ No API key provided."
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("selected_model", "meta/llama-3.1-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ API Error: {str(e)}"

# ====================== MAIN APP ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. **AI-Powered with NVIDIA NIM**.")

# AI Job Finder Button (Hackathon Requirement)
st.markdown("### 🚀 AI Job Finder")
col_find1, col_find2 = st.columns([3, 1])
with col_find1:
    query = st.text_input(
        "Describe the job you want (e.g. warehouse jobs at WMN7 in North Mankato, MN)",
        placeholder="Warehouse jobs at WMN7 in North Mankato, MN"
    )
with col_find2:
    if st.button("🔍 Find Open Jobs", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Calling NVIDIA NIM to find jobs..."):
                prompt = f"""
                You are a job search assistant. Search for and list real-looking open job postings 
                matching this query: "{query}".
                Return results in JSON format as a list of objects with keys:
                title, company, location, salary, type, description, requirements, benefits.
                Make up plausible data based on the query. Limit to 3-5 results.
                """
                result = call_nvidia_llm(prompt, temperature=0.6)
                try:
                    new_jobs = json.loads(result)
                    if isinstance(new_jobs, list):
                        new_df = pd.DataFrame(new_jobs)
                        # Add missing columns
                        for col in ["id", "posted", "match", "website", "phone", "referrer"]:
                            if col not in new_df.columns:
                                new_df[col] = [str(uuid.uuid4()) if col=="id" else 
                                              datetime.now().strftime("%Y-%m-%d") if col=="posted" else 
                                              85 if col=="match" else "" for _ in range(len(new_df))]
                        st.session_state.jobs = pd.concat([st.session_state.jobs, new_df], ignore_index=True)
                        st.success(f"Added {len(new_df)} new AI-generated job postings!")
                        st.rerun()
                except:
                    st.info("Raw LLM response (could not parse JSON):")
                    st.write(result)

# Filters (keep original + search)
st.markdown("### ■ Discover Your Next Role")
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    search = st.text_input("■ Search titles, skills, companies...", placeholder="Amazon Flex, warehouse")
with col2:
    location_filter = st.selectbox("■ Location", ["All Locations", "North Mankato"])
with col3:
    job_type = st.selectbox("■ Type", ["All Types", "Part Time >19 hours a week"])
with col4:
    min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)

# Filtering logic (unchanged)
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

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

st.caption(f"Showing **{len(df)}** high-quality opportunities")

# Job Cards (unchanged)
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
                <span class="badge">Match: {job['match']}%</span>
            </div>

            <div class="info-label">Description</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('description', '')}</div>

            <div class="info-label">Requirements</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('requirements', '')}</div>

            <div class="info-label">Benefits</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">{job.get('benefits', '')}</div>

            <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                <div><strong>Website:</strong> <a href="{job.get('website', '#')}" target="_blank" style="color:#6e8cff;">{job.get('website', 'N/A')}</a></div>
                <div><strong>Phone:</strong> {job.get('phone', 'N/A')}</div>
            </div>

            <div style="margin-top:16px; padding-top:12px; border-top:1px solid #334477; font-size:0.9rem; color:#8899cc;">
                <strong>Referred By:</strong> {job.get('referrer', 'N/A')}
            </div>
        </div>
        """)

        col_a, col_b = st.columns([1, 4])
        with col_a:
            st.link_button(
                label="🚀 Apply Now",
                url=job.get("website", "#"),
                use_container_width=True
            )

# ====================== AI CHAT SECTION ======================
st.markdown("---")
st.subheader("💬 Chat with AI Assistant about Jobs")

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message ai-msg"><strong>AI ({st.session_state.selected_model}):</strong> {msg["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask about a job, salary negotiation, or anything else..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking with NVIDIA NIM..."):
        context = f"Current jobs available: {df.to_dict(orient='records')[:5]}" if not df.empty else "No jobs currently loaded."
        full_prompt = f"""
        You are a helpful job search assistant. Use the following context:
        {context}
        
        User question: {prompt}
        Give a friendly, useful answer.
        """
        ai_response = call_nvidia_llm(full_prompt, temperature=0.7)
    
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    st.rerun()

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "Open Job Postings • Modern job platform prototype with NVIDIA NIM"
    "</p>",
    unsafe_allow_html=True
)
