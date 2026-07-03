import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

st.set_page_config(page_title="AltIndeed", layout="wide")

# Session state for persistence (jobs, applications)
if "jobs" not in st.session_state:
    st.session_state.jobs = pd.DataFrame([
        {"id": str(uuid.uuid4()), "title": "Senior Python Engineer", "company": "TechCorp", 
         "location": "Remote", "salary": "120k-160k", "skills": "Python, Django, AWS", 
         "posted": "2026-07-01", "type": "Full-time"},
        {"id": str(uuid.uuid4()), "title": "Marketing Manager", "company": "GrowthCo", 
         "location": "New York", "salary": "80k-110k", "skills": "SEO, Content", 
         "posted": "2026-07-02", "type": "Full-time"},
    ])

if "applications" not in st.session_state:
    st.session_state.applications = []

# Sidebar Navigation
page = st.sidebar.selectbox("Navigate", 
    ["🏠 Home", "🔍 Job Search", "📝 Post a Job", "📬 My Applications", "👔 Employer Dashboard", "🤖 AI Matcher"])

st.title("AltIndeed - Better Jobs, Less Spam")

if page == "🏠 Home":
    st.header("Welcome to the anti-Indeed")
    st.write("Quality matches. Transparent salaries. Real feedback.")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Jobs Posted", len(st.session_state.jobs))
    with col2:
        st.metric("Happy Seekers", "247")  # fake

elif page == "🔍 Job Search":
    st.header("Find Jobs")
    
    col1, col2, col3 = st.columns(3)
    search = col1.text_input("Search keywords")
    location = col2.text_input("Location / Remote")
    salary_min = col3.number_input("Min Salary (k)", value=50)
    
    df = st.session_state.jobs.copy()
    if search:
        df = df[df['title'].str.contains(search, case=False) | 
                df['skills'].str.contains(search, case=False)]
    if location:
        df = df[df['location'].str.contains(location, case=False)]
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if not df.empty:
        job_id = st.selectbox("Select a job to apply", df["title"])
        if st.button("Apply Now"):
            st.success(f"Application sent for {job_id}! (In real version this would email + track)")
            st.session_state.applications.append({"job": job_id, "date": datetime.now()})

elif page == "📝 Post a Job":
    st.header("Post a New Job")
    with st.form("post_job"):
        title = st.text_input("Job Title")
        company = st.text_input("Company")
        location = st.text_input("Location")
        salary = st.text_input("Salary Range")
        skills = st.text_input("Key Skills (comma separated)")
        job_type = st.selectbox("Type", ["Full-time", "Part-time", "Contract", "Remote"])
        
        submitted = st.form_submit_button("Post Job")
        if submitted and title:
            new_job = {
                "id": str(uuid.uuid4()),
                "title": title,
                "company": company or "Your Company",
                "location": location,
                "salary": salary,
                "skills": skills,
                "posted": datetime.now().strftime("%Y-%m-%d"),
                "type": job_type
            }
            st.session_state.jobs = pd.concat([st.session_state.jobs, pd.DataFrame([new_job])], ignore_index=True)
            st.success("Job posted!")

elif page == "📬 My Applications":
    st.header("My Applications")
    if st.session_state.applications:
        for app in st.session_state.applications:
            st.write(f"✅ {app['job']} - Applied on {app['date'].strftime('%Y-%m-%d')}")
    else:
        st.info("No applications yet. Go search for jobs!")

elif page == "👔 Employer Dashboard":
    st.header("Employer Dashboard")
    st.write("Posted Jobs:")
    st.dataframe(st.session_state.jobs, use_container_width=True)
    st.metric("Total Applications", len(st.session_state.applications))

elif page == "🤖 AI Matcher":
    st.header("AI Smart Matcher (Demo)")
    resume = st.text_area("Paste your resume or skills summary")
    if st.button("Find Best Matches"):
        if resume:
            st.success("AI Analysis:")
            st.write("Top matches based on your skills:")
            matches = st.session_state.jobs.sample(min(3, len(st.session_state.jobs)))
            for _, job in matches.iterrows():
                st.write(f"**{job['title']}** at {job['company']} — Match: 92%")
        else:
            st.warning("Enter some skills!")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Prototype built with Streamlit. Next: real DB (Supabase), auth, real AI.")
