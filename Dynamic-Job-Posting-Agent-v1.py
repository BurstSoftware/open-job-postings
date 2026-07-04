import streamlit as st

st.set_page_config(
    page_title="Dynamic Job Posting Agent",
    page_icon="💼",
    layout="centered"
)

st.title("💼 Dynamic Job Posting Agent")
st.markdown("Generate professional, ready-to-post job listings in seconds.")

with st.form("job_form"):
    st.subheader("Company Information")
    
    col1, col2 = st.columns(2)
    with col1:
        business_name = st.text_input("Business Name *", placeholder="Acme Solutions Inc.")
    with col2:
        website = st.text_input("Business Website", placeholder="https://www.acmesolutions.com")
    
    phone = st.text_input("Company Phone Number", placeholder="(555) 123-4567")

    st.subheader("Job Details")
    
    job_title = st.text_input("Job Title *", placeholder="Senior Marketing Manager")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        city = st.text_input("City *", placeholder="Austin")
    with col4:
        state = st.text_input("State *", placeholder="TX")
    with col5:
        zip_code = st.text_input("Zip Code", placeholder="78701")

    job_type = st.selectbox(
        "Job Type *",
        ["Full Time", "Part Time", "Salary"],
        index=0
    )

    st.subheader("Compensation")
    
    hourly_rate = None
    monthly_rate = None
    
    if job_type == "Salary":
        monthly_rate = st.number_input(
            "Monthly Pay Rate ($)", 
            min_value=0.0, 
            value=6500.0, 
            step=100.0,
            format="%.2f"
        )
    else:
        hourly_rate = st.number_input(
            "Hourly Pay Rate ($)", 
            min_value=0.0, 
            value=28.50, 
            step=0.50,
            format="%.2f"
        )

    st.subheader("Additional Details (Optional but Recommended)")
    
    job_description = st.text_area(
        "Job Description / Key Responsibilities",
        placeholder="Write a short description of the role...",
        height=130
    )
    
    requirements = st.text_area(
        "Requirements / Qualifications",
        placeholder="List required experience, skills, education...",
        height=130
    )
    
    benefits = st.text_area(
        "Benefits (Optional)",
        placeholder="Health insurance, 401(k), PTO, remote work, etc.",
        height=80
    )

    submitted = st.form_submit_button("🚀 Generate Job Posting", use_container_width=True)

# ==================== GENERATE POSTING ====================
if submitted:
    if not business_name or not job_title or not city or not state:
        st.error("Please fill in all required fields (marked with *)")
    else:
        # Format location
        location = f"{city}, {state}"
        if zip_code:
            location += f" {zip_code}"
        
        # Format pay
        if monthly_rate is not None:
            pay_text = f"${monthly_rate:,.2f} per month"
        else:
            pay_text = f"${hourly_rate:,.2f} per hour"
        
        # Build the dynamic job posting
        posting = f"""# 🚀 **Now Hiring: {job_title}**

**{business_name}** is currently seeking a motivated **{job_title}** to join our team in **{location}**.

### Position Overview
- **Job Type:** {job_type}
- **Compensation:** {pay_text}
- **Location:** {location}

"""

        if job_description.strip():
            posting += f"""### About the Role
{job_description.strip()}

"""

        if requirements.strip():
            posting += f"""### Requirements
{requirements.strip()}

"""

        if benefits.strip():
            posting += f"""### Benefits & Perks
{benefits.strip()}

"""

        posting += f"""### How to Apply
Please visit our website: **{website if website else '[Your Website]'}**  
Or call us at **{phone if phone else '[Company Phone]'}**

We look forward to receiving your application!

---
*Generated with Dynamic Job Posting Agent*
"""

        # Display results
        st.success("✅ Job posting generated successfully!")
        
        st.markdown("### 📋 Live Preview")
        st.markdown(posting)
        
        st.divider()
        
        # Copy-paste friendly version
        st.markdown("### 📋 Copy & Paste Version")
        st.text_area(
            "Full Job Posting (copy from here)",
            value=posting,
            height=450,
            label_visibility="collapsed"
        )
        
        # Download buttons
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            st.download_button(
                label="📥 Download as .txt",
                data=posting,
                file_name=f"{job_title.replace(' ', '_')}_Job_Posting.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_dl2:
            st.download_button(
                label="📥 Download as Markdown (.md)",
                data=posting,
                file_name=f"{job_title.replace(' ', '_')}_Job_Posting.md",
                mime="text/markdown",
                use_container_width=True
            )
