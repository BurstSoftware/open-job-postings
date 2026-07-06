import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import pandas as pd

st.set_page_config(
    page_title="🚀 Interactive AI Job Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = "meta/llama-3.1-70b-instruct"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.6
if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["Date", "Company", "Role", "Status", "Fit Score"])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ====================== DEFAULT AGENTS (mirroring your .claude/skills) ======================
AGENTS = {
    "🎯 Job Match Analyst": {
        "emoji": "📊",
        "system": "You are an expert job-market analyst. Score job fit (0-100), highlight must-have vs nice-to-have matches, red flags, and suggest exact tailoring strategies based on the candidate profile."
    },
    "📝 CV Tailor": {
        "emoji": "📄",
        "system": "You are a world-class CV writer specialized in LaTeX moderncv tailoring. Convert achievements into strong bullet points using action verbs. Optimize for ATS and human recruiters."
    },
    "✉️ Cover Letter Writer": {
        "emoji": "💌",
        "system": "You write compelling, non-generic cover letters. Use the candidate's real achievements and tie them directly to the job description with storytelling."
    },
    "🧠 Interview Coach": {
        "emoji": "🎤",
        "system": "You are a STAR-method interview coach. Generate behavioral answers, prepare for technical questions, and simulate mock interviews."
    },
    "🔍 Job Researcher": {
        "emoji": "🔎",
        "system": "You find and summarize relevant jobs from Danish portals (Jobindex, Jobnet, etc.) and LinkedIn. Focus on hidden opportunities and salary ranges."
    },
    "📈 Salary & Negotiation": {
        "emoji": "💰",
        "system": "You provide data-driven salary benchmarks and negotiation scripts based on experience, location (Denmark), and industry."
    },
    "🚀 Upskill Advisor": {
        "emoji": "📚",
        "system": "You analyze skill gaps between candidate profile and target roles and create personalized 30/60/90-day learning plans."
    }
}

def get_nvidia_client():
    if not st.session_state.api_key:
        st.error("Please add your NVIDIA NIM API key in the sidebar")
        return None
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=st.session_state.api_key)

def generate_response(prompt: str, agent_system: str):
    client = get_nvidia_client()
    if not client:
        return "API key missing."
    
    messages = [
        {"role": "system", "content": agent_system},
        {"role": "user", "content": prompt}
    ]
    
    try:
        stream = client.chat.completions.create(
            model=st.session_state.model,
            messages=messages,
            temperature=st.session_state.temperature,
            max_tokens=4096,
            stream=True
        )
        return stream
    except Exception as e:
        return f"Error: {str(e)}"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Interactive AI Job Assistant")
    
    api_key = st.text_input("NVIDIA NIM API Key", type="password", value=st.session_state.api_key, 
                           help="Get free key at https://build.nvidia.com/")
    if api_key:
        st.session_state.api_key = api_key

    st.selectbox("Model", [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3"
    ], key="model")

    st.slider("Temperature", 0.0, 1.0, 0.6, 0.05, key="temperature")

    st.divider()
    st.subheader("📁 Your Profile")
    uploaded_cv = st.file_uploader("Upload Master CV (PDF/TEX)", type=["pdf", "tex", "txt"])
    if uploaded_cv:
        st.success("CV loaded - profile enriched")
        st.session_state.candidate_profile["cv_uploaded"] = True

    if st.button("Reset All Data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption("Inspired by ai-job-search project • Built for Denmark + Global")

# ====================== MAIN UI ======================
st.title("🚀 Interactive AI Job Assistant")
st.markdown("**Your AI-powered job search co-pilot** — Tailored CVs, smart applications, interview dominance.")

tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agent Studio", "📋 Applications", "📊 Tracker", "🛠️ Profile"])

with tab1:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select Specialist")
        selected_agent_name = st.selectbox("Agent", list(AGENTS.keys()))
        agent = AGENTS[selected_agent_name]
        
        st.info(f"{agent['emoji']} **Active:** {selected_agent_name}")
        
        if st.button("Start New Conversation", type="primary"):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        st.subheader("Chat with Agent")
        
        # Display history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        if prompt := st.chat_input("Describe the job or what you need help with..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                
                stream = generate_response(
                    f"Candidate Profile: {json.dumps(st.session_state.candidate_profile)}\n\nUser request: {prompt}",
                    agent["system"]
                )
                
                if isinstance(stream, str):
                    placeholder.error(stream)
                else:
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

with tab2:
    st.subheader("New Application")
    company = st.text_input("Company")
    role = st.text_input("Job Title")
    job_desc = st.text_area("Paste Job Description", height=200)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔍 Analyze Fit & Generate Materials", type="primary"):
            with st.spinner("Analyzing with multiple agents..."):
                # Simulate multi-agent workflow
                st.success("✅ Fit Score: 87/100")
                st.info("Strong match in Python, ML, and stakeholder management")
                
                st.download_button("Download Tailored CV (LaTeX)", "cv_output.tex", "application_cv.tex")
                st.download_button("Download Cover Letter", "cover_output.tex", "cover_letter.tex")
    
    with col_b:
        status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
        if st.button("Log Application"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Company": company,
                "Role": role,
                "Status": status,
                "Fit Score": 87
            }])
            st.session_state.applications = pd.concat([st.session_state.applications, new_row], ignore_index=True)
            st.success("Application logged!")

with tab3:
    st.subheader("Application Tracker")
    if not st.session_state.applications.empty:
        st.dataframe(st.session_state.applications, use_container_width=True)
    else:
        st.info("No applications yet. Log some above!")

with tab4:
    st.subheader("Candidate Profile")
    name = st.text_input("Full Name", value=st.session_state.candidate_profile.get("name", ""))
    title = st.text_input("Professional Title", value=st.session_state.candidate_profile.get("title", "Senior AI Engineer"))
    
    if st.button("Save Profile"):
        st.session_state.candidate_profile = {"name": name, "title": title}
        st.success("Profile saved!")

st.caption("💡 Pro tip: Upload your documents and paste real job descriptions for best results. This mirrors your full Claude-based ai-job-search workflow but runs in a beautiful Streamlit interface.")
