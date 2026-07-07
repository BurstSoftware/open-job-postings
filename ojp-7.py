import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Open Job Postings",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }
    
    /* Beautiful Job Cards */
    .job-card { 
        background: linear-gradient(145deg, #16213e, #1e2a5c); 
        border-radius: 20px; 
        padding: 24px; 
        margin: 16px 0; 
        border: 1px solid #4a5d9e; 
        transition: all 0.3s ease; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
    }
    .job-card:hover { 
        transform: translateY(-8px); 
        box-shadow: 0 20px 40px rgba(74,93,158,0.4); 
        border-color: #6e8cff; 
    }
    .job-title { font-size: 1.45rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
    .company { color: #8f9eff; font-weight: 600; font-size: 1.1rem; }
    .badge { 
        display: inline-block; 
        background: #3a4a8c; 
        color: #c0d0ff; 
        padding: 6px 14px; 
        border-radius: 30px; 
        font-size: 0.85rem; 
        margin-right: 10px; 
        margin-bottom: 8px; 
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

st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)
st.markdown("Discover real opportunities from the community dataset")

# Load data
@st.cache_data
def load_jobs_from_github():
    url = "https://raw.githubusercontent.com/BurstSoftware/open-job-postings/main/jobs.csv"
    try:
        df = pd.read_csv(url)
        expected_cols = ["id", "title", "company", "location", "salary", "posted", 
                        "type", "match", "website", "phone", "description", 
                        "requirements", "benefits", "referrer"]
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
                
        df['match'] = pd.to_numeric(df['match'], errors='coerce').fillna(0).astype(int)
        df['posted'] = pd.to_datetime(df['posted'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame(columns=["title", "company"])

df = load_jobs_from_github()

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")
search_term = st.sidebar.text_input("Search jobs", placeholder="Title, company, keywords...")
min_match = st.sidebar.slider("Minimum Match Score (%)", 0, 100, 0)

# Apply filters
filtered_df = df.copy()
if search_term:
    mask = (
        filtered_df['title'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['company'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['description'].astype(str).str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

filtered_df = filtered_df[filtered_df['match'] >= min_match]
filtered_df = filtered_df.sort_values(by='match', ascending=False).reset_index(drop=True)

st.sidebar.caption(f"Showing {len(filtered_df)} of {len(df)} jobs")

# Display Beautiful Job Cards
st.header(f"Featured Jobs ({len(filtered_df)})")

if filtered_df.empty:
    st.info("No jobs match your filters. Try lowering the match score or clearing the search.")
else:
    for i, job in filtered_df.iterrows():
        st.html(f"""
        <div class="job-card">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <div class="job-title">{job.get('title', 'N/A')}</div>
                    <div class="company">■ {job.get('company', 'N/A')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.3rem; font-weight:700; color:#00ff9d;">
                        {job.get('salary', 'N/A')}
                    </div>
                    <div style="color:#8899cc;">{job.get('location', 'N/A')}</div>
                </div>
            </div>
            
            <div style="margin: 20px 0 16px 0; display: flex; flex-wrap: wrap; gap: 12px;">
                <span class="badge">{job.get('type', 'N/A')}</span>
                <span class="badge">Match: {int(job.get('match', 0))}%</span>
                <span class="badge">Posted: {job['posted'].date() if pd.notna(job.get('posted')) else 'N/A'}</span>
            </div>
            
            <div style="color:#b0b8ff; line-height:1.6; margin-bottom:12px;">
                <strong>Description:</strong> {job.get('description', 'No description provided.')}
            </div>
            
            <div style="color:#b0b8ff; line-height:1.6; margin-bottom:12px;">
                <strong>Requirements:</strong> {job.get('requirements', 'N/A')}
            </div>
            
            <div style="color:#b0b8ff; line-height:1.6; margin-bottom:20px;">
                <strong>Benefits:</strong> {job.get('benefits', 'N/A')}
            </div>
            
            <div style="display:flex; gap:24px; font-size:0.95rem; color:#8899cc; border-top:1px solid #334477; padding-top:14px;">
                <div><strong>Website:</strong> 
                    <a href="{job.get('website', '#')}" target="_blank" style="color:#6e8cff;">Apply Now →</a>
                </div>
                <div><strong>Phone:</strong> {job.get('phone', 'N/A')}</div>
                <div><strong>Referrer:</strong> {job.get('referrer', 'N/A')}</div>
            </div>
        </div>
        """)

st.divider()
st.caption("Data sourced from BurstSoftware/open-job-postings on GitHub")
