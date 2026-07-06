import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Candidate Profile Tool",
    page_icon="🧑‍💼",
    layout="wide"
)

st.title("🧑‍💼 Candidate Profile Builder")
st.caption("Create a clean, structured candidate profile ready to paste into any AI job search tool.")

# Initialize session state
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("Profile Management")

    if st.button("📝 Load Sample Fictional Profile", use_container_width=True):
        sample = {
            "target_job_title": "Senior Software Engineer - AI/ML",
            "years_of_experience": 7,
            "education": "- B.S. Computer Science, State University (2017)\n- Relevant coursework: Machine Learning, Algorithms, Distributed Systems",
            "skills": "Python, TensorFlow, PyTorch, AWS (SageMaker, Lambda, EC2), Docker, Kubernetes, SQL, Git, CI/CD, Agile/Scrum",
            "certifications": "AWS Certified Machine Learning – Specialty (2023)\nGoogle Professional Machine Learning Engineer (2022)",
            "experience_summary": "7+ years building and scaling AI/ML systems. Currently leading a team of 5 engineers developing recommendation and personalization engines for a large e-commerce platform. Previously worked at two startups in backend and full-stack roles.",
            "accomplishments": "- Designed and productionized an ML model that improved recommendation CTR by 28% and generated an estimated $2.1M in additional annual revenue.\n- Led migration from monolithic architecture to microservices, reducing deployment time from days to under 30 minutes.\n- Mentored 4 junior engineers and contributed to open-source ML tooling (500+ GitHub stars).",
            "preferred_industries": "Technology, E-commerce, Fintech, AI/ML-focused companies",
            "preferred_job_functions": "Machine Learning Engineering, AI Software Engineering, Technical Leadership",
            "location_preferences": "Fully remote or hybrid in SF Bay Area, NYC, Austin, or Seattle",
            "work_arrangement": "Fully Remote",
            "salary_expectations": "$165,000 – $210,000 base + equity/bonus",
            "additional_notes": "Strong preference for companies with mature engineering culture, good work-life balance, and opportunities to work on production AI systems. Open to both individual contributor and light leadership roles.",
            "generated_at": datetime.now().isoformat()
        }
        st.session_state.profile_data = sample
        st.rerun()

    uploaded_file = st.file_uploader("Upload saved JSON profile", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state.profile_data = json.load(uploaded_file)
            st.success("Profile loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load file: {e}")

    if st.button("🗑️ Clear Current Profile", use_container_width=True):
        st.session_state.profile_data = {}
        st.rerun()

# ===================== MAIN FORM =====================
st.header("1. Enter / Edit Candidate Profile")

with st.form("profile_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        target_job_title = st.text_input(
            "Target Job Title / Position *",
            value=st.session_state.profile_data.get("target_job_title", ""),
            placeholder="e.g. Senior Machine Learning Engineer"
        )

        years_of_experience = st.number_input(
            "Total Years of Professional Experience *",
            min_value=0,
            max_value=50,
            step=1,
            value=st.session_state.profile_data.get("years_of_experience", 0)
        )

        education = st.text_area(
            "Education Background",
            value=st.session_state.profile_data.get("education", ""),
            height=120,
            placeholder="• B.S. Computer Science, University Name (Year)\n• M.S. Data Science, University Name (Year)"
        )

        skills = st.text_area(
            "Relevant Skills",
            value=st.session_state.profile_data.get("skills", ""),
            height=120,
            placeholder="Python, TensorFlow, AWS, Docker, SQL, Project Management, etc."
        )

        certifications = st.text_area(
            "Certifications",
            value=st.session_state.profile_data.get("certifications", ""),
            height=80,
            placeholder="AWS Certified Solutions Architect (2023)\nPMP (2021)"
        )

    with col2:
        experience_summary = st.text_area(
            "Professional Experience Summary",
            value=st.session_state.profile_data.get("experience_summary", ""),
            height=160,
            placeholder="Brief overview of career progression and key responsibilities..."
        )

        accomplishments = st.text_area(
            "Key Accomplishments & Achievements",
            value=st.session_state.profile_data.get("accomplishments", ""),
            height=140,
            placeholder="• Increased revenue by X%\n• Led team of Y people\n• Reduced costs by Z%"
        )

        preferred_industries = st.text_area(
            "Preferred Industries",
            value=st.session_state.profile_data.get("preferred_industries", ""),
            height=70,
            placeholder="Technology, Fintech, Healthcare, E-commerce"
        )

        preferred_job_functions = st.text_area(
            "Preferred Job Functions",
            value=st.session_state.profile_data.get("preferred_job_functions", ""),
            height=70,
            placeholder="Software Engineering, Data Science, Product Management"
        )

    location_preferences = st.text_input(
        "Location Preferences",
        value=st.session_state.profile_data.get("location_preferences", ""),
        placeholder="Fully remote, Hybrid in NYC, Open to relocation to Austin/Seattle"
    )

    work_arrangement = st.selectbox(
        "Preferred Work Arrangement",
        ["Fully Remote", "Hybrid", "On-site", "No Preference"],
        index=["Fully Remote", "Hybrid", "On-site", "No Preference"].index(
            st.session_state.profile_data.get("work_arrangement", "Fully Remote")
        )
    )

    salary_expectations = st.text_input(
        "Salary Expectations (optional)",
        value=st.session_state.profile_data.get("salary_expectations", ""),
        placeholder="$140,000 – $180,000 + equity"
    )

    additional_notes = st.text_area(
        "Additional Notes / Context (optional)",
        value=st.session_state.profile_data.get("additional_notes", ""),
        height=80,
        placeholder="Any other details useful for job matching (e.g. willingness to travel, company culture preferences, etc.)"
    )

    submitted = st.form_submit_button(
        "🚀 Generate / Update Formatted Profile",
        type="primary",
        use_container_width=True
    )

# ===================== PROCESS SUBMISSION =====================
if submitted:
    profile = {
        "target_job_title": target_job_title,
        "years_of_experience": years_of_experience,
        "education": education,
        "skills": skills,
        "certifications": certifications,
        "experience_summary": experience_summary,
        "accomplishments": accomplishments,
        "preferred_industries": preferred_industries,
        "preferred_job_functions": preferred_job_functions,
        "location_preferences": location_preferences,
        "work_arrangement": work_arrangement,
        "salary_expectations": salary_expectations,
        "additional_notes": additional_notes,
        "generated_at": datetime.now().isoformat()
    }
    st.session_state.profile_data = profile
    st.success("Profile updated successfully!")

# ===================== DISPLAY GENERATED PROFILE =====================
if st.session_state.profile_data and st.session_state.profile_data.get("target_job_title"):
    st.divider()
    st.header("2. Ready-to-Use Profile (Copy & Paste)")

    data = st.session_state.profile_data

    # Markdown version (best for AI)
    md_text = f"""# CANDIDATE PROFILE

**Target Job Title / Position:** {data.get('target_job_title', 'Not specified')}
**Total Years of Experience:** {data.get('years_of_experience', 0)}

## Education Background
{data.get('education') or 'Not specified'}

## Relevant Skills
{data.get('skills') or 'Not specified'}

## Certifications
{data.get('certifications') or 'Not specified'}

## Professional Experience Summary
{data.get('experience_summary') or 'Not specified'}

## Key Accomplishments & Achievements
{data.get('accomplishments') or 'Not specified'}

## Job Preferences
- **Preferred Industries:** {data.get('preferred_industries') or 'Not specified'}
- **Preferred Job Functions:** {data.get('preferred_job_functions') or 'Not specified'}
- **Location Preferences:** {data.get('location_preferences') or 'Not specified'}
- **Work Arrangement:** {data.get('work_arrangement', 'Not specified')}
- **Salary Expectations:** {data.get('salary_expectations') or 'Open to discussion'}

## Additional Notes
{data.get('additional_notes') or 'None'}

---
*Profile generated on {data.get('generated_at', 'N/A')} | Use this block with your AI job search tools.*
"""

    st.subheader("📋 Markdown Version (Recommended)")
    st.code(md_text, language="markdown")

    # JSON version
    json_text = json.dumps(data, indent=2)
    st.subheader("📦 JSON Version (for structured prompts or automation)")
    st.code(json_text, language="json")

    # Download buttons
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "⬇️ Download Markdown (.md)",
            data=md_text,
            file_name="candidate_profile.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            "⬇️ Download JSON (.json)",
            data=json_text,
            file_name="candidate_profile.json",
            mime="application/json",
            use_container_width=True
        )

    st.info("**Tip:** Paste the Markdown version at the top of your prompt to any AI job search tool, e.g.:\n\n`Here is my candidate profile:\n[PASTE MARKDOWN ABOVE]\n\nNow analyze this job description for fit...`")

st.caption("This tool contains no personal data by default. All information is entered by you.")
