# ojp-1-3.py
import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import re

# ====================== CONFIG ======================
st.set_page_config(
    page_title="AltIndeed",
    page_icon="■",  # Valid emoji
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
.match-bar {
    height: 6px;
    background: linear-gradient(90deg, #00ff9d, #00ccff);
    border-radius: 10px;
    margin: 12px 0;
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

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **AltIndeed**")
    st.caption("Modern jobs. Zero spam.")
    
    page = st.selectbox(
        "Navigate",
        ["■ Home", "■ Discover Jobs", "■ Post a Job", "■ My Applications",
         "■ Employer Hub", "■ AI Matcher"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.button("■■ Clear All Data (Dev)", use_container_width=True):
        st.session_state.jobs = st.session_state.jobs.iloc[:0]
        st.session_state.applications = []
        st.rerun()
    
    st.markdown("---")
    st.info("Prototype • Built with ❤■ for better hiring", icon="■")

# ====================== MAIN APP ======================
st.markdown('<h1 class="header-title">AltIndeed</h1>', unsafe_allow_html=True)
st.markdown("**Quality over quantity.** Transparent. Modern. Actually good.")

if page == "■ Home":
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### Welcome to the future of job hunting")
        st.write("No endless scrolling. No ghosting. Just great matches.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Active Jobs", len(st.session_state.jobs), "↑3 today")
    with c2:
        st.metric("Matches Made", "1,284", "↑18%")
    with c3:
        st.metric("Avg Salary", "$128k", "↑4%")
    with c4:
        st.metric("Satisfaction", "98%", "★★★★★")
    
    st.image("https://picsum.photos/id/1015/1200/400", use_column_width=True)

elif page == "■ Discover Jobs":
    # Discover Jobs UI has been removed per requirements.
    # Menu entry is preserved for future iterations.
    st.markdown("### ■ Discover Jobs")
    st.info("🔧 The Discover Jobs experience is being rebuilt. Check back soon!")
    
    st.markdown("**In the meantime, explore other sections:**")
    st.markdown("- Use **Post a Job** to list new roles")
    st.markdown("- View your applications in **My Applications**")
    st.markdown("- Try the **AI Matcher** for smart recommendations")

elif page == "■ Post a Job":
    st.markdown("### ■ Post a New Role")
    with st.form("post_job_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Job Title *", placeholder="Senior Backend Engineer")
            company = st.text_input("Company Name *", placeholder="Your Company")
            location = st.text_input("Location", value="Remote")
        with c2:
            salary = st.text_input("Salary Range", placeholder="130k–180k")
            job_type = st.selectbox("Employment Type", ["Full-time", "Contract", "Part-time", "Internship"])
            skills = st.text_input("Key Skills (comma separated)", placeholder="Python, AWS, React")
        
        description = st.text_area("Job Description / What you'll do", height=180)
        
        submitted = st.form_submit_button("Post Job", use_container_width=True)
        
        if submitted and title and company:
            new_job = {
                "id": str(uuid.uuid4()),
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "skills": skills,
                "posted": datetime.now().strftime("%Y-%m-%d"),
                "type": job_type,
                "match": 0
            }
            st.session_state.jobs = pd.concat([st.session_state.jobs, pd.DataFrame([new_job])], ignore_index=True)
            st.success("Job posted successfully! It’s now live.")

elif page == "■ My Applications":
    st.markdown("### ■ Your Applications")
    if st.session_state.applications:
        for app in reversed(st.session_state.applications):
            st.success(f"**{app['job']}** \n{app['company']} • Applied {app['date'].strftime('%b %d, %Y')}")
    else:
        st.info("You haven't applied to any roles yet. Start exploring!")

elif page == "■ Employer Hub":
    st.markdown("### ■ Employer Dashboard")
    st.dataframe(
        st.session_state.jobs[['title', 'company', 'location', 'salary', 'type']],
        use_container_width=True,
        hide_index=True
    )
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Jobs Posted", len(st.session_state.jobs))
    with col2:
        st.metric("Total Applications Received", len(st.session_state.applications))

elif page == "■ AI Matcher":
    st.markdown("### ■ AI Smart Matcher")
    st.write("Paste your experience and let AI find your best fits.")
    resume = st.text_area("Your resume / skills summary", 
                         height=220,
                         placeholder="5+ years Python • Built scalable Django apps • AWS certified...")
    
    if st.button("Find My Best Matches", type="primary", use_container_width=True):
        if resume:
            with st.spinner("Analyzing your profile..."):
                st.success("AI Match Complete")
                matches = st.session_state.jobs.sort_values(by='match', ascending=False).head(3)
                for _, job in matches.iterrows():
                    match_score = job['match']
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <div class="job-title">{job['title']}</div>
                                <div class="company">{job['company']} • {job['location']}</div>
                            </div>
                            <div style="text-align:right; font-size:2rem; font-weight:800; color:#00ff9d;">
                                {match_score}%
                            </div>
                        </div>
                        <div class="match-bar" style="width:{match_score}%"></div>
                        <small>{job['skills']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter your skills or resume text.")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6677aa; font-size:0.9rem;'>"
    "AltIndeed • A modern job platform prototype • Made with Streamlit + ❤■"
    "</p>",
    unsafe_allow_html=True
)
