import streamlit as st
import pandas as pd
import uuid
import re

# ====================== CONFIG & CSS ======================
st.set_page_config(
    page_title="Job Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
.job-card { background: linear-gradient(145deg, #16213e, #1e2a5c); border-radius: 20px; padding: 24px; margin: 16px 0; 
            border: 1px solid #4a5d9e; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.job-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(74,93,158,0.4); border-color: #6e8cff; }
.job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
.company { color: #8f9eff; font-weight: 600; }
.badge { display: inline-block; background: #3a4a8c; color: #c0d0ff; padding: 4px 12px; border-radius: 30px; 
         font-size: 0.8rem; margin-right: 8px; }
.info-label { font-weight: 600; color: #8899cc; margin-top: 16px; margin-bottom: 6px; font-size: 0.95rem; }
.header-title { font-size: 2.8rem; background: linear-gradient(90deg, #a0c4ff, #c0d0ff); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "jobs" not in st.session_state:
    jobs_list = [
        {
            "id": str(uuid.uuid4()),
            "title": "Amazon Flex - X / L1",
            "company": "Amazon",
            "location": "North Mankato, MN",
            "salary": "$19/hr",
            "posted": "2026-07-04",
            "type": "Part Time",
            "match": 78,
            "website": "https://www.amazon.com/getpaid",
            "phone": "N/A",
            "description": "Picking, Packing, Sorting, Stowing in a fast-paced warehouse environment.",
            "requirements": "Lifting up to 49lbs, twisting, bending, stooping. Must have reliable transportation.",
            "benefits": "Flexible hours, benefits through A to Z app, weekly pay.",
            "referrer": "narossoh"
        }
    ]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "saved_search_filters" not in st.session_state:
    st.session_state.saved_search_filters = {
        "search": "",
        "location": "All Locations",
        "job_type": "All Types",
        "min_salary": 30000
    }

if "applications" not in st.session_state:
    st.session_state.applications = []

# ====================== HELPER FUNCTIONS ======================
def extract_salary_value(s):
    s = str(s).lower().replace('$', '').replace(',', '').strip()
    match = re.search(r'(\d+(?:\.\d+)?)\s*(k|hr|hour| /hr)?', s)
    if not match:
        nums = re.findall(r'\d+', s)
        return int(nums[0]) if nums else 0
    val = float(match.group(1))
    unit = match.group(2) or ''
    if 'k' in unit:
        val *= 1000
    elif 'hr' in unit or 'hour' in unit:
        val *= 2080
    return int(val)

def apply_filters_to_jobs(filters):
    df = st.session_state.jobs.copy()
    if filters["search"]:
        df = df[
            df['title'].str.contains(filters["search"], case=False, na=False) | 
            df['company'].str.contains(filters["search"], case=False, na=False) |
            df['description'].str.contains(filters["search"], case=False, na=False)
        ]
    if filters["location"] != "All Locations":
        df = df[df['location'].str.contains(filters["location"], case=False, na=False)]
    if filters["job_type"] != "All Types":
        df = df[df['type'].str.contains(filters["job_type"], case=False, na=False)]
    
    df = df[df['salary'].apply(extract_salary_value) >= filters["min_salary"]]
    df = df.sort_values(by="match", ascending=False)
    return df

US_STATES = ["All Locations", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
             "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
             "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
             "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", 
             "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", 
             "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
             "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", 
             "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

JOB_TYPES = ["All Types", "Full Time", "Part Time", "Contract", "Remote"]

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Job Studio**")
    st.caption("Modern jobs. Zero spam.")
    st.divider()

    st.subheader("🔍 Search & Filters")
    st.caption("50-State Job Board")

    st.divider()
    st.caption("Prototype • Built with Streamlit")

# ====================== MAIN PAGE ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
st.markdown("### ■ Discover Your Next Role")

filters = st.session_state.saved_search_filters

with st.expander("🔍 Refine Search Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search keywords", value=filters["search"])
    with col2:
        loc_index = US_STATES.index(filters["location"]) if filters["location"] in US_STATES else 0
        location = st.selectbox("Location", US_STATES, index=loc_index)
    with col3:
        type_index = JOB_TYPES.index(filters["job_type"]) if filters["job_type"] in JOB_TYPES else 0
        job_type = st.selectbox("Job Type", JOB_TYPES, index=type_index)
    
    min_sal = st.slider("Minimum Annual Salary ($)", 0, 300000, filters["min_salary"], step=5000)
    
    if st.button("Apply Filters", use_container_width=True):
        st.session_state.saved_search_filters = {
            "search": search,
            "location": location,
            "job_type": job_type,
            "min_salary": min_sal
        }
        st.rerun()

df = apply_filters_to_jobs(st.session_state.saved_search_filters)
st.caption(f"Showing **{len(df)}** opportunities")

if df.empty:
    st.warning("No jobs match your filters.")
else:
    for _, job in df.iterrows():
        st.markdown(f"""
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
                <div style="margin-top: 10px;">
                    <span class="badge">Match: {job.get('match', 80)}%</span>
                </div>
            </div>
            <div class="info-label">Description</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('description','')}</div>
            <div class="info-label">Requirements</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">{job.get('requirements','')}</div>
            <div class="info-label">Benefits</div>
            <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">{job.get('benefits','')}</div>
            <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
                <div><strong>Website:</strong> <a href="{job.get('website','#')}" target="_blank" style="color:#6e8cff;">Apply Link</a></div>
                <div><strong>Phone:</strong> {job.get('phone','N/A')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, _ = st.columns([1, 4])
        with col_a:
            if st.button("🚀 Apply Now", key=f"apply_{job['id']}"):
                st.session_state.applications.append(job.to_dict())
                st.success("✅ Application submitted!")
