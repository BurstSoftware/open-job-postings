import streamlit as st
import pandas as pd
import uuid
import re
import json
from io import StringIO

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (your original) ======================
st.markdown("""<style> ... your existing CSS here ... </style>""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()
    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input("NVIDIA API Key (nvapi-...)", type="password", value=st.session_state.get("nvidia_api_key", ""))
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()
    
    model_options = ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", 
                     "nvidia/nemotron-4-340b-instruct", "deepseek-ai/deepseek-v3"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)
    st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature")
    
    st.divider()
    if st.button("🔄 Refresh Jobs", use_container_width=True):
        if "jobs" in st.session_state:
            del st.session_state.jobs
        st.rerun()

# ====================== JOB DATA (GitHub Alternative + Fallback) ======================
CSV_DATA = """id,title,company,location,salary,posted,type,match,website,phone,description,requirements,benefits,referrer
,Amazon Flex - X,Amazon,North Mankato, MN 56003,$19/hr,2026-07-04,Part Time >19 hours a week,92,http://amazon.com/getpaid,N/a,Picking, packing, sorting, stowing,Lifting up to 49lbs, twisting, bending, stooping,Benefits available through the A to Z app,narossoh"""

@st.cache_data(ttl=300)
def load_jobs():
    try:
        # Try GitHub first (replace with your real raw URL later)
        # GITHUB_URL = "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/jobs.csv"
        # df = pd.read_csv(GITHUB_URL)
        
        # Current fallback using the data you provided
        df = pd.read_csv(StringIO(CSV_DATA))
        
        # Auto-generate ID if empty
        df['id'] = df['id'].fillna([str(uuid.uuid4()) for _ in range(len(df))])
        
        return df
    except Exception as e:
        st.error(f"Error loading jobs: {e}")
        return pd.DataFrame()

# Load jobs
if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs()

# ====================== REST OF YOUR CODE (unchanged) ======================
# ... Keep all your AGENTS, helper functions, tabs, etc. ...

# In TAB 1 - Discover Jobs, update the caption:
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    st.caption(f"📊 Loaded **{len(st.session_state.jobs)}** job opportunities")
    
    # ... rest of your filtering and job card display code remains the same ...
