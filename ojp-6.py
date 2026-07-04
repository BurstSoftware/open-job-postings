import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import io

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
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
</style>
""", unsafe_allow_html=True)

# ====================== LOAD CSV DATA ======================
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
        "description": "warehouse work",
        "requirements": "warehouse work",
        "benefits": "benefits available through the A to Z app",
        "referrer": "narossoh"
    })

if "jobs" not in st.session_state:
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam.")
    st.divider()
    if st.button("Clear All Data (Dev)", use_container_width=True):
        st.session_state.jobs = pd.DataFrame(jobs_list)
        st.session_state.applications = []
        st.rerun()
    st.markdown("---")
    st.info("Prototype • Built with ❤️ for better hiring", icon="ℹ️")

# ====================== MAIN APP ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. Actually good.")

# Filters
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

# Filtering
df = st.session_state.jobs.copy()
if search:
    df = df[
        df['title'].str.contains(search, case=False) | 
        df['company'].str.contains(search, case=False) |
        df['description'].str.contains(search, case=False)
    ]
if location_filter != "All Locations":
    df = df[df['location'].str.contains(location_filter, case=False)]
if job_type != "All Types":
    df = df[df['type'] == job_type]

def extract_min_salary(s):
    nums = re.findall(r'\d+', s)
    return int(nums[0]) if nums else 0

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

st.caption(f"Showing **{len(df)}** high-quality opportunities")

# ====================== JOB CARDS ======================
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
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job['description']}</div>

            <div class="info-label">Requirements</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job['requirements']}</div>

            <div class="info-label">Benefits</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">{job['benefits']}</div>

            <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                <div><strong>Website:</strong> <a href="{job['website']}" target="_blank" style="color:#6e8cff;">amazon.com/getpaid</a></div>
                <div><strong>Phone:</strong> {job['phone']}</div>
            </div>

            <div style="margin-top:16px; padding-top:12px; border-top:1px solid #334477; font-size:0.9rem; color:#8899cc;">
                <strong>Referred By:</strong> {job['referrer']}
            </div>
        </div>
        """)

        # Apply Now Button - Direct Link (No redirect message)
        col_a, col_b = st.columns([1, 4])
        with col_a:
            st.link_button(
                label="🚀 Apply Now",
                url=job["website"],
                use_container_width=True
            )

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "Open Job Postings • Modern job platform prototype"
    "</p>",
    unsafe_allow_html=True
)
