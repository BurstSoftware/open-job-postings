import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re
import time

# ====================== CONFIG ======================
st.set_page_config(
    page_title="AltIndeed Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
/* App Background */
.stApp {
    background: radial-gradient(circle at top right, #1a1a2e 0%, #0f0f1a 100%);
    color: #e0e0ff;
}

/* Glassmorphism Job Cards */
.job-card {
    background: rgba(30, 42, 92, 0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    margin: 16px 0;
    border: 1px solid rgba(110, 140, 255, 0.15);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.job-card:hover {
    transform: translateY(-5px);
    background: rgba(40, 55, 115, 0.35);
    border-color: #00ff9d;
    box-shadow: 0 12px 40px rgba(0, 255, 157, 0.15);
}

/* Typography */
.job-title {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ffffff, #a0c4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}

.company {
    color: #8f9eff;
    font-weight: 600;
    font-size: 1.1rem;
    letter-spacing: 0.5px;
}

/* Badges */
.badge-container {
    margin: 16px 0;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    background: rgba(110, 140, 255, 0.1);
    border: 1px solid rgba(110, 140, 255, 0.3);
    color: #c0d0ff;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge.match {
    background: rgba(0, 255, 157, 0.1);
    border-color: #00ff9d;
    color: #00ff9d;
}

/* Header */
.header-title {
    font-size: 3.5rem;
    background: linear-gradient(135deg, #00ff9d, #00b8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    margin-bottom: 0;
    padding-bottom: 0;
}

/* Placeholder Banner */
.demo-placeholder {
    background: linear-gradient(90deg, rgba(255, 0, 127, 0.1), rgba(0, 255, 157, 0.1));
    border-left: 4px solid #ff007f;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 24px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "jobs" not in st.session_state:
    st.session_state.jobs = pd.DataFrame([
        {
            "id": str(uuid.uuid4()),
            "title": "Senior Python Engineer",
            "company": "TechCorp",
            "location": "Remote",
            "salary": "$120k–$160k",
            "skills": "Python, Django, AWS, PostgreSQL",
            "posted": "2026-07-01",
            "type": "Full-time",
            "match": 94
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Growth Marketing Manager",
            "company": "GrowthCo",
            "location": "New York, NY",
            "salary": "$85k–$115k",
            "skills": "SEO, Content Strategy, Analytics",
            "posted": "2026-07-02",
            "type": "Full-time",
            "match": 87
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Product Designer",
            "company": "Nexus Studio",
            "location": "San Francisco",
            "salary": "$130k–$170k",
            "skills": "Figma, User Research, Prototyping",
            "posted": "2026-07-03",
            "type": "Full-time",
            "match": 91
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Amazon Associate - WMN7 Flex",
            "company": "Amazon",
            "location": "North Mankato, MN 56003",
            "salary": "$19/hr",
            "skills": "Warehouse, Picking, Packing, Flexible Schedule",
            "posted": "2026-07-04",
            "type": "Part-time",
            "match": 98
        }
    ])

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("## ⚡ **AltIndeed Pro**")
    st.caption("Next-Gen Tech Hiring.")
    st.divider()
    
    # Dashboard stats
    st.metric("Total Applications", len(st.session_state.applications))
    st.metric("Profile Match Score", "92%", "+4% this week")
    
    st.divider()
    if st.button("Reset Environment", type="primary", use_container_width=True):
        st.session_state.jobs = st.session_state.jobs.iloc[:0]
        st.session_state.applications = []
        st.rerun()
        
    st.markdown("---")
    st.info("Alpha v2.0 • Cyber Theme", icon="🌌")

# ====================== MAIN APP ======================
st.markdown('<h1 class="header-title">AltIndeed</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #8899cc; font-size: 1.2rem;'>Find your next hyper-growth opportunity.</p>", unsafe_allow_html=True)

# ====================== SEARCH & FILTERS ======================
with st.container():
    st.markdown("### 🔍 Search Matrix")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    with col1:
        search = st.text_input("Keywords", placeholder="React, Remote, Amazon...", label_visibility="collapsed")

    with col2:
        location = st.selectbox("Location", ["All Locations", "Remote", "New York", "San Francisco", "North Mankato, MN"], label_visibility="collapsed")

    with col3:
        job_type = st.selectbox("Type", ["All Types", "Full-time", "Contract", "Part-time"], label_visibility="collapsed")

    with col4:
        # Changed min value to 0 so hourly jobs don't get filtered out immediately
        min_salary = st.slider("Min Salary/Rate", 0, 200, 0, format="%d", help="Filters both hourly ($) and yearly (k)")

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

def extract_min_salary(s):
    # Extracts the first number it finds, handling both hourly and yearly
    nums = re.findall(r'\d+', s.replace('k', '').replace('$', ''))
    return int(nums[0]) if nums else 0

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

# ====================== PLACEHOLDER ======================
# As requested: A placeholder injected right before the job tiles
st.markdown("""
<div class="demo-placeholder">
    <div><b>🛠️ UI PLACEHOLDER:</b> This space is reserved for a featured sponsor banner, AI-driven career insights, or a custom hero component before the main job feed begins.</div>
</div>
""", unsafe_allow_html=True)

# ====================== JOB TILES ======================
st.markdown(f"### ⚡ Top Matches ({len(df)})")

if df.empty:
    st.warning("No opportunities match your current matrix parameters. Try expanding your search.")
else:
    # Sort by match score to prioritize the best fits (like the Amazon demo job)
    df = df.sort_values(by="match", ascending=False)
    
    for _, job in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="job-title">{job['title']}</div>
                        <div class="company">🏢 {job['company']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.4rem; font-weight:800; color:#00ff9d; letter-spacing: 1px;">{job['salary']}</div>
                        <div style="font-size:0.9rem; color:#a0c4ff; margin-top: 4px;">📍 {job['location']}</div>
                    </div>
                </div>
                <div class="badge-container">
                    <span class="badge match">🎯 {job['match']}% Match</span>
                    <span class="badge">💼 {job['type']}</span>
                    <span class="badge">⏱️ Posted {job['posted']}</span>
                </div>
                <div style="color:#b0b8ff; font-size:1rem; margin-top:12px; border-top: 1px solid rgba(110,140,255,0.1); padding-top: 12px;">
                    <strong>Tech Stack / Skills:</strong> {job['skills']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns([1, 1, 4])
            with col_a:
                # Using Streamlit's new button types for a cooler look
                if st.button("⚡ Apply Now", key=f"apply_{job['id']}", type="primary", use_container_width=True):
                    st.session_state.applications.append({
                        "job": job['title'],
                        "company": job['company'],
                        "date": datetime.now()
                    })
                    # Toast is much cooler/modern than balloons
                    st.toast(f"Application securely transmitted to {job['company']}!", icon="🚀")
            
            with col_b:
                st.button("Save", key=f"save_{job['id']}", use_container_width=True)

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#4a5d9e; font-size:0.85rem; font-family: monospace;'>"
    "SYSTEM.ALT_INDEED.V2 // 2026 // END OF FEED"
    "</p>",
    unsafe_allow_html=True
)
