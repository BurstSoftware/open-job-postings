import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re

# ====================== CONFIG ======================
st.set_page_config(
    page_title="AltIndeed",
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
.stApp {
    background: #0f0f23;
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
.match-badge {
    display: inline-block;
    background: linear-gradient(90deg, #00ff9d, #00cc7a);
    color: #000;
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 0.9rem;
    font-weight: 700;
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

# ====================== SESSION STATE ======================
if "jobs" not in st.session_state:
    st.session_state.jobs = pd.DataFrame([
        {
            "id": str(uuid.uuid4()),
            "title": "Amazon Associate - WMN7 Flex",
            "company": "Amazon",
            "location": "North Mankato, MN 56003",
            "salary": "$19/hr",
            "skills": "Warehouse, Picking, Packing, Flexible Schedule",
            "posted": "2026-07-04",
            "type": "Part-time",
            "match": 82
        }
    ])

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **AltIndeed**")
    st.caption("Modern jobs. Zero spam.")
    st.divider()
    if st.button("Clear All Data (Dev)", use_container_width=True):
        st.session_state.jobs = st.session_state.jobs.iloc[:0]
        st.session_state.applications = []
        st.rerun()
    st.markdown("---")
    st.info("Prototype • Built with ❤️ for better hiring", icon="ℹ️")

# ====================== MAIN APP ======================
st.markdown('<h1 class="header-title">AltIndeed</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. Actually good.")

# ====================== DISCOVER JOBS ======================
st.markdown("### ■ Discover Your Next Role")
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    search = st.text_input("■ Search titles, skills, companies...", 
                          placeholder="Senior Engineer, React, Remote, Amazon")

with col2:
    location = st.selectbox("■ Location", 
                           ["All Locations", "Remote", "New York", "San Francisco", "London", "North Mankato, MN"])

with col3:
    job_type = st.selectbox("■ Type", 
                           ["All Types", "Full-time", "Contract", "Part-time"])

with col4:
    min_salary = st.slider("■ Min Salary (k)", 50, 250, 80)

# Filter logic
df = st.session_state.jobs.copy()

if search:
    df = df[
        df['title'].str.contains(search, case=False) | 
        df['skills'].str.contains(search, case=False) | 
        df['company'].str.contains(search, case=False) |
        df['location'].str.contains(search, case=False)
    ]

if location != "All Locations":
    df = df[df['location'].str.contains(location, case=False)]

if job_type != "All Types":
    df = df[df['type'] == job_type]

# Improved salary filter - handles hourly and annual
def extract_min_salary(s):
    # Remove $ and /hr
    clean = s.replace('$', '').replace('/hr', '').replace('k', '').strip()
    nums = re.findall(r'\d+', clean)
    val = int(nums[0]) if nums else 0
    # If it's hourly, convert roughly to annual (40hrs * 52 weeks)
    if '/hr' in s.lower():
        val = val * 40 * 52 // 1000  # convert to k
    return val

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

st.caption(f"Showing **{len(df)}** high-quality opportunities")

if df.empty:
    st.warning("No jobs match your filters. Try broadening your search!")
else:
    for _, job in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="job-title">{job['title']}</div>
                        <div class="company">■ {job['company']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.1rem; font-weight:700; color:#00ff9d;">{job['salary']}</div>
                        <div style="font-size:0.85rem; color:#8899cc;">{job['location']}</div>
                    </div>
                </div>
                
                <div style="margin:16px 0;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <span class="match-badge">Match: {job['match']}%</span>
                </div>
                
                <div style="color:#b0b8ff; font-size:0.95rem; margin:12px 0;">
                    <strong>Skills:</strong> {job['skills']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns([1, 4])
            with col_a:
                if st.button("Apply Now", key=f"apply_{job['id']}", use_container_width=True):
                    st.session_state.applications.append({
                        "job": job['title'],
                        "company": job['company'],
                        "date": datetime.now()
                    })
                    st.success(f"Application sent to **{job['company']}** for **{job['title']}**!")
                    st.balloons()

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "AltIndeed • Discover Jobs • Modern job platform prototype"
    "</p>",
    unsafe_allow_html=True
)
