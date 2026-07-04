import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re

# ====================== CONFIG ======================
st.set_page_config(page_title="AltIndeed", page_icon="■", layout="wide")

# ====================== CATEGORIES ======================
CATEGORIES = {
    "All Categories": "All", "Tech": "💻 Tech", "Business": "📊 Business",
    "Trade": "🔧 Trade & Skilled", "Creative": "🎨 Creative",
    "Healthcare": "🩺 Healthcare", "Sales": "💼 Sales",
    "Education": "📚 Education", "Other": "🔀 Other"
}

CATEGORY_COLORS = {
    "Tech": "#00d4ff", "Business": "#9d4edd", "Trade": "#ff9500",
    "Creative": "#ff4d94", "Healthcare": "#4ade80", "Sales": "#facc15",
    "Education": "#60a5fa", "Other": "#94a3b8"
}

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
.job-card {
    background: linear-gradient(145deg, #16213e, #1e2a5c);
    border-radius: 20px;
    padding: 24px;
    margin: 16px 0;
    border: 1px solid #4a5d9e;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}
.job-card:hover { transform: translateY(-8px); border-color: #6e8cff; }
.job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; }
.company { color: #8f9eff; font-weight: 600; }
.badge {
    display: inline-block; padding: 4px 12px; border-radius: 30px;
    font-size: 0.85rem; margin-right: 8px;
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
        {"id": str(uuid.uuid4()), "title": "Senior Python Engineer", "company": "TechCorp", "location": "Remote",
         "salary": "120k–160k", "skills": "Python, Django, AWS, PostgreSQL", "posted": "2026-07-01",
         "type": "Full-time", "match": 94, "category": "Tech"},
        {"id": str(uuid.uuid4()), "title": "Growth Marketing Manager", "company": "GrowthCo", "location": "New York, NY",
         "salary": "85k–115k", "skills": "SEO, Content Strategy, Analytics", "posted": "2026-07-02",
         "type": "Full-time", "match": 87, "category": "Business"},
        {"id": str(uuid.uuid4()), "title": "Product Designer", "company": "Nexus Studio", "location": "San Francisco",
         "salary": "130k–170k", "skills": "Figma, User Research, Prototyping", "posted": "2026-07-03",
         "type": "Full-time", "match": 91, "category": "Creative"},
        {"id": str(uuid.uuid4()), "title": "Amazon Associate - WMN7 Flex", "company": "Amazon",
         "location": "North Mankato, MN 56003", "salary": "$19/hr",
         "skills": "Warehouse, Picking, Packing", "posted": "2026-07-04",
         "type": "Part-time", "match": 82, "category": "Trade"},
        {"id": str(uuid.uuid4()), "title": "Journeyman Electrician", "company": "PowerGrid Solutions",
         "location": "Chicago, IL", "salary": "75k–95k",
         "skills": "Electrical Systems, Blueprint Reading", "posted": "2026-07-03",
         "type": "Full-time", "match": 89, "category": "Trade"},
    ])

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">AltIndeed</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. Actually good.")

st.markdown("### ■ Discover Your Next Role")
col1, col2, col3, col4, col5 = st.columns([3, 1.8, 1.8, 1.8, 1.8])

with col1:
    search = st.text_input("Search titles, skills, companies...", placeholder="Python, Remote, Marketing")
with col2:
    category = st.selectbox("Category", options=list(CATEGORIES.keys()))
with col3:
    location = st.selectbox("Location", ["All Locations", "Remote", "New York", "San Francisco", "Chicago", "North Mankato, MN"])
with col4:
    job_type = st.selectbox("Type", ["All Types", "Full-time", "Part-time", "Contract"])
with col5:
    min_salary = st.slider("Min Salary (k)", 0, 250, 50)

# ====================== FILTERING ======================
df = st.session_state.jobs.copy()

if search:
    df = df[df['title'].str.contains(search, case=False) |
            df['skills'].str.contains(search, case=False) |
            df['company'].str.contains(search, case=False)]

if category != "All Categories":
    df = df[df['category'] == category]

if location != "All Locations":
    df = df[df['location'].str.contains(location, case=False)]

if job_type != "All Types":
    df = df[df['type'] == job_type]

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s).replace('k', '').replace('$', ''))
    return int(nums[0]) if nums else 0

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

st.caption(f"**{len(df)}** opportunities found")

# ====================== DISPLAY JOBS ======================
if df.empty:
    st.error("No jobs found. Try clearing some filters.")
    st.dataframe(st.session_state.jobs, use_container_width=True)  # Debug fallback
else:
    for _, job in df.iterrows():
        color = CATEGORY_COLORS.get(job['category'], "#6b7280")
        
        st.markdown(f"""
        <div class="job-card">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <div class="job-title">{job['title']}</div>
                    <div class="company">■ {job['company']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.2rem; font-weight:700; color:#00ff9d;">{job['salary']}</div>
                    <div style="color:#8899cc;">{job['location']}</div>
                </div>
            </div>
            
            <div style="margin:12px 0;">
                <span class="badge" style="background:{color};">{job['category']}</span>
                <span class="badge">{job['type']}</span>
                <span class="badge">Posted {job['posted']}</span>
                <span class="badge" style="background:#22c55e; color:black;">{job['match']}% Match</span>
            </div>
            
            <div><strong>Skills:</strong> {job['skills']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Apply Now", key=f"apply_{job['id']}"):
            st.success(f"Application sent to **{job['company']}** for **{job['title']}**! 🎉")
            st.balloons()

# ====================== DEBUG SECTION ======================
with st.expander("🔍 Debug: Show All Raw Jobs Data"):
    st.dataframe(st.session_state.jobs, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#6677aa;'>AltIndeed Prototype</p>", unsafe_allow_html=True)
