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

# ====================== CATEGORIES ======================
CATEGORIES = {
    "All Categories": "All",
    "Tech": "💻 Tech",
    "Business": "📊 Business",
    "Trade": "🔧 Trade & Skilled",
    "Creative": "🎨 Creative",
    "Healthcare": "🩺 Healthcare",
    "Sales": "💼 Sales",
    "Education": "📚 Education",
    "Other": "🔀 Other"
}

CATEGORY_COLORS = {
    "Tech": "#00d4ff",
    "Business": "#9d4edd",
    "Trade": "#ff9500",
    "Creative": "#ff4d94",
    "Healthcare": "#4ade80",
    "Sales": "#facc15",
    "Education": "#60a5fa",
    "Other": "#94a3b8"
}

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    color: #e0e0ff;
}
.stApp { background: #0f0f23; }
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
.company { color: #8f9eff; font-weight: 600; }
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
    background: #22c55e;
    color: black;
    font-weight: 700;
}
.stButton>button {
    border-radius: 50px;
    height: 48px;
    font-weight: 600;
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
            "title": "Senior Python Engineer",
            "company": "TechCorp",
            "location": "Remote",
            "salary": "120k–160k",
            "skills": "Python, Django, AWS, PostgreSQL",
            "posted": "2026-07-01",
            "type": "Full-time",
            "match": 94,
            "category": "Tech"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Growth Marketing Manager",
            "company": "GrowthCo",
            "location": "New York, NY",
            "salary": "85k–115k",
            "skills": "SEO, Content Strategy, Analytics",
            "posted": "2026-07-02",
            "type": "Full-time",
            "match": 87,
            "category": "Business"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Product Designer",
            "company": "Nexus Studio",
            "location": "San Francisco",
            "salary": "130k–170k",
            "skills": "Figma, User Research, Prototyping",
            "posted": "2026-07-03",
            "type": "Full-time",
            "match": 91,
            "category": "Creative"
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
            "match": 82,
            "category": "Trade"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Journeyman Electrician",
            "company": "PowerGrid Solutions",
            "location": "Chicago, IL",
            "salary": "75k–95k",
            "skills": "Electrical Systems, Blueprint Reading, Safety Protocols",
            "posted": "2026-07-03",
            "type": "Full-time",
            "match": 89,
            "category": "Trade"
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

# ====================== FILTERS ======================
st.markdown("### ■ Discover Your Next Role")
col1, col2, col3, col4, col5 = st.columns([3, 1.8, 1.8, 1.8, 1.8])

with col1:
    search = st.text_input("■ Search titles, skills, companies...", 
                          placeholder="Senior Engineer, React, Remote, Amazon")

with col2:
    category = st.selectbox("■ Category", options=list(CATEGORIES.keys()))

with col3:
    location = st.selectbox("■ Location", 
                           ["All Locations", "Remote", "New York", "San Francisco", "London", "North Mankato, MN", "Chicago"])

with col4:
    job_type = st.selectbox("■ Type", 
                           ["All Types", "Full-time", "Part-time", "Contract"])

with col5:
    min_salary = st.slider("■ Min Salary (k)", 0, 250, 60)

# ====================== FILTER LOGIC ======================
df = st.session_state.jobs.copy()

if search:
    df = df[
        df['title'].str.contains(search, case=False) | 
        df['skills'].str.contains(search, case=False) | 
        df['company'].str.contains(search, case=False) |
        df['location'].str.contains(search, case=False)
    ]

if category != "All Categories":
    df = df[df['category'] == category]

if location != "All Locations":
    df = df[df['location'].str.contains(location, case=False)]

if job_type != "All Types":
    df = df[df['type'] == job_type]

def extract_min_salary(s):
    nums = re.findall(r'\d+', s.replace('k', '').replace('$', '').replace('/hr', ''))
    return int(nums[0]) if nums else 0

df = df[df['salary'].apply(extract_min_salary) >= min_salary]

st.caption(f"Showing **{len(df)}** high-quality opportunities")

# ====================== DISPLAY JOBS ======================
if df.empty:
    st.warning("No jobs match your filters. Try broadening your search!")
else:
    for _, job in df.iterrows():
        color = CATEGORY_COLORS.get(job.get('category'), "#6b7280")
        cat_name = CATEGORIES.get(job.get('category'), job.get('category', 'Other'))
        
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
                    <span class="badge" style="background:{color};">{cat_name}</span>
                    <span class="badge">{job['type']}</span>
                    <span class="badge">Posted {job['posted']}</span>
                    <span class="badge match-badge">Match: {job['match']}%</span>
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
                        "date": datetime.now(),
                        "category": job.get('category')
                    })
                    st.success(f"✅ Application sent to **{job['company']}**!")
                    st.balloons()

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "AltIndeed • Discover Jobs • Modern job platform prototype"
    "</p>",
    unsafe_allow_html=True
)
