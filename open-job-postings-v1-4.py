import streamlit as st
import pandas as pd
import uuid

st.set_page_config(
    page_title="AltIndeed",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (from ojp-1-3) ======================
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
.match-bar {
    height: 6px;
    background: linear-gradient(90deg, #00ff9d, #00ccff);
    border-radius: 10px;
    margin: 12px 0;
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

# ====================== INITIAL DATA ======================
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
            "match": 94
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
            "match": 87
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
            "match": 91
        }
    ])

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 💼 **AltIndeed**")
    st.caption("Modern jobs. Zero spam.")
    st.divider()
    if st.button("Reset to Sample Data", use_container_width=True):
        st.session_state.jobs = pd.DataFrame([
            {"id": str(uuid.uuid4()), "title": "Senior Python Engineer", "company": "TechCorp", "location": "Remote", "salary": "120k–160k", "skills": "Python, Django, AWS, PostgreSQL", "posted": "2026-07-01", "type": "Full-time", "match": 94},
            {"id": str(uuid.uuid4()), "title": "Growth Marketing Manager", "company": "GrowthCo", "location": "New York, NY", "salary": "85k–115k", "skills": "SEO, Content Strategy, Analytics", "posted": "2026-07-02", "type": "Full-time", "match": 87},
            {"id": str(uuid.uuid4()), "title": "Product Designer", "company": "Nexus Studio", "location": "San Francisco", "salary": "130k–170k", "skills": "Figma, User Research, Prototyping", "posted": "2026-07-03", "type": "Full-time", "match": 91}
        ])
        st.rerun()
    st.info("Prototype • Beautiful Card View Only", icon="💼")

# ====================== MAIN HEADER ======================
st.markdown('<h1 class="header-title">AltIndeed</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. Actually good.")

# ====================== DISCOVER JOBS SECTION ======================
st.markdown("### Discover Your Next Role")

# Filters
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    search = st.text_input("🔍 Search titles, skills, companies...", placeholder="Senior Engineer, Python, Remote")
with col2:
    location_filter = st.selectbox("📍 Location", ["All Locations", "Remote", "New York, NY", "San Francisco"])
with col3:
    min_match = st.slider("⭐ Minimum Match %", 0, 100, 70)

# Apply filters
df = st.session_state.jobs.copy()
if search:
    df = df[
        df['title'].str.contains(search, case=False) |
        df['skills'].str.contains(search, case=False) |
        df['company'].str.contains(search, case=False)
    ]
if location_filter != "All Locations":
    df = df[df['location'].str.contains(location_filter, case=False)]

df = df[df['match'] >= min_match]
df = df.sort_values(by='match', ascending=False)

st.caption(f"Showing {len(df)} high-quality opportunities")

# ====================== BEAUTIFUL CARDS ======================
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
                        <div class="company">💼 {job['company']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.6rem; font-weight:700; color:#00ff9d;">{job['match']}%</div>
                        <div style="font-size:1.1rem; color:#a0c4ff;">{job['salary']}</div>
                    </div>
                </div>
                
                <div style="margin:16px 0;">
                    <span class="badge">{job['type']}</span>
                    <span class="badge">📍 {job['location']}</span>
                    <span class="badge">📅 {job['posted']}</span>
                </div>
                
                <div style="color:#b0b8ff; margin:12px 0;">
                    <strong>🛠️ Skills:</strong> {job['skills']}
                </div>
                
                <div class="match-bar" style="width:{job['match']}%"></div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "AltIndeed • Beautiful Card View Prototype</p>",
    unsafe_allow_html=True
)
