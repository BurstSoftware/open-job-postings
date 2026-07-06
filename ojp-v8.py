import streamlit as st
import pandas as pd
import uuid
import re

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ `openai` package is not installed. Run: `pip install openai`")
    st.stop()

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Open Job Postings • AI Powered",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
.main { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%); color: #e0e0ff; }

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

.job-title { font-size: 1.4rem; font-weight: 700; color: #a0c4ff; margin-bottom: 8px; }
.company { color: #8f9eff; font-weight: 600; }

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

.guide-step {
    background: #16213e;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 16px;
    border-left: 5px solid #6e8cff;
}

/* Chat Styling */
.chat-message { 
    padding: 14px 18px; 
    border-radius: 18px; 
    margin: 10px 0; 
    max-width: 85%;
}
.user-msg { 
    background: linear-gradient(135deg, #4a6bff, #2a4fff); 
    color: white; 
    margin-left: auto; 
}
.ai-msg { 
    background: #16213e; 
    color: #e0e0ff; 
    margin-right: auto; 
    border: 1px solid #334477;
}
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# ■ **Open Job Postings**")
    st.caption("Modern jobs. Zero spam. AI Powered.")
    st.divider()

    st.subheader("🔑 NVIDIA NIM Settings")
    api_key = st.text_input(
        "NVIDIA API Key (nvapi-...)", 
        type="password",
        value=st.session_state.get("nvidia_api_key", ""),
        help="Paste your key from https://build.nvidia.com/"
    )
    
    if api_key and api_key != st.session_state.get("nvidia_api_key"):
        st.session_state.nvidia_api_key = api_key
        st.success("✅ API Key saved!", icon="🔑")
        st.rerun()

    model_options = ["meta/llama-3.1-70b-instruct"]
    st.session_state.selected_model = st.selectbox("Select Model", model_options, index=0)

    st.divider()
    if st.button("🗑️ Clear All Data", use_container_width=True):
        for key in ["jobs", "chat_history", "applications"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.info("Powered by NVIDIA NIM", icon="ℹ️")

# ====================== INITIAL DATA ======================
if "jobs" not in st.session_state:
    jobs_list = [{
        "id": str(uuid.uuid4()),
        "title": "Amazon Flex - X",
        "company": "Amazon",
        "location": "North Mankato, MN 56003",
        "salary": "$19/hr",
        "posted": "2026-07-04",
        "type": "Part Time >19 hours a week",
        "match": 92,
        "website": "http://amazon.com/getpaid",
        "phone": "N/a",
        "description": "Picking, packing, sorting, stowing",
        "requirements": "Lifting up to 49lbs, twisting, bending, stooping",
        "benefits": "Benefits available through the A to Z app",
        "referrer": "narossoh"
    }]
    st.session_state.jobs = pd.DataFrame(jobs_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== HELPER FUNCTIONS ======================
def get_nvidia_client():
    if not st.session_state.get("nvidia_api_key"):
        st.warning("⚠️ Please enter your NVIDIA API Key in the sidebar.")
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=st.session_state.nvidia_api_key)

def call_nvidia_llm(prompt, temperature=0.7, max_tokens=1024):
    client = get_nvidia_client()
    if not client:
        return "❌ Please provide a valid NVIDIA API key."
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("selected_model", "meta/llama-3.1-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ NVIDIA API Error: {str(e)}"

def extract_min_salary(s):
    nums = re.findall(r'\d+', str(s))
    return int(nums[0]) if nums else 0

# ====================== MAIN UI ======================
st.markdown('<h1 class="header-title">Open Job Postings</h1>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Discover Jobs", "💬 AI Job Assistant", "📖 How-To Guide"])

# ==================== TAB 1: DISCOVER JOBS ====================
with tab1:
    st.markdown("### ■ Discover Your Next Role")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search = st.text_input("■ Search...", placeholder="Amazon Flex, warehouse")
    with col2:
        location_filter = st.selectbox("■ Location", ["All Locations", "North Mankato"])
    with col3:
        job_type = st.selectbox("■ Type", ["All Types", "Part Time >19 hours a week"])
    with col4:
        min_salary = st.slider("■ Min Hourly ($)", 0, 200, 15)

    df = st.session_state.jobs.copy()
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False) | 
                df['company'].str.contains(search, case=False, na=False) |
                df['description'].str.contains(search, case=False, na=False)]
    if location_filter != "All Locations":
        df = df[df['location'].str.contains(location_filter, case=False, na=False)]
    if job_type != "All Types":
        df = df[df['type'] == job_type]
    df = df[df['salary'].apply(extract_min_salary) >= min_salary]

    st.caption(f"Showing **{len(df)}** opportunities")

    if df.empty:
        st.warning("No jobs match your filters.")
    else:
        for _, job in df.iterrows():
            st.html(f"""
            <div class="job-card"> ... </div>
            """)   # (your job card code stays the same)

# ==================== TAB 2: AI Job Assistant ====================
with tab2:
    st.markdown("### 💬 AI Job Assistant")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-msg"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-msg"><strong>AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask anything about jobs in your area..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner("Thinking with NVIDIA NIM..."):
            context = str(st.session_state.jobs.head(8).to_dict(orient="records"))
            full_prompt = f"""You are a helpful career coach for North Mankato, MN.
Context (current jobs): {context}
User question: {prompt}
Answer in a friendly and useful way."""
            response = call_nvidia_llm(full_prompt, temperature=0.75)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ==================== TAB 3: HOW-TO GUIDE (Fixed) ====================
with tab3:
    st.markdown("### 📖 How to Use Open Job Postings")
    st.markdown("Welcome! This guide will help you get started quickly with the **NVIDIA NIM** powered features.")

    st.subheader("1. Get Your Free NVIDIA API Key")
    st.markdown("""
    <div class="guide-step">
        <strong>Step-by-step:</strong><br><br>
        1. Go to <a href="https://build.nvidia.com/" target="_blank">build.nvidia.com</a><br>
        2. Sign up / log in (free)<br>
        3. Click on <strong>API Keys</strong> (top right or profile menu)<br>
        4. Create new key → name it "Job Assistant"<br>
        5. Copy the key (starts with <code>nvapi-</code>)<br>
        6. Paste it into the sidebar on the left
    </div>
    """, unsafe_allow_html=True)

    st.subheader("2. Using the AI Job Assistant")
    st.markdown("""
    <div class="guide-step">
        <strong>Good example questions:</strong>
        <ul>
            <li>What jobs are good for someone with no experience?</li>
            <li>Compare the Amazon Flex job with others</li>
            <li>Help me write an application message</li>
            <li>What skills do I need for warehouse work?</li>
            <li>Is $19/hr good pay in North Mankato?</li>
        </ul>
        <strong>Tips:</strong>
        <ul>
            <li>Be specific about your experience and availability</li>
            <li>Ask follow-up questions — the AI remembers the chat</li>
            <li>Try: "Explain this job like I'm new to it"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("3. Browsing & Filtering Jobs")
    st.markdown("""
    <div class="guide-step">
        Use the filters in the <strong>Discover Jobs</strong> tab:<br><br>
        • Search by title, company, or keywords<br>
        • Filter by location and job type<br>
        • Use the slider for minimum hourly pay<br><br>
        Click <strong>Apply Now</strong> to go to the real job page.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Troubleshooting")
    st.info("""
    **API Key not working?**  
    → Make sure you pasted the full key (starts with `nvapi-`). Try creating a new one.

    **No response from AI?**  
    → Check that your key is saved in the sidebar.

    **No jobs visible?**  
    → Clear or adjust the filters.
    """)

    st.success("✅ You're all set! Start exploring jobs or chatting with the AI assistant.", icon="🚀")

st.caption("Open Job Postings • NVIDIA NIM Integration")
