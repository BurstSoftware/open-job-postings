import streamlit as st
import pandas as pd
import uuid

st.set_page_config(page_title="Job Board", page_icon="💼", layout="wide")

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

# ====================== TITLE & FILTERS ======================
st.title("💼 Job Board")
st.markdown("Beautiful Card View")

# Simple filters
col1, col2 = st.columns([3, 1])
with col1:
    search = st.text_input("🔍 Search by title, company or skills", "")
with col2:
    min_match = st.slider("Minimum Match %", 0, 100, 0)

# Apply filters
df = st.session_state.jobs.copy()
if search:
    mask = (
        df["title"].str.contains(search, case=False, na=False) |
        df["company"].str.contains(search, case=False, na=False) |
        df["skills"].str.contains(search, case=False, na=False)
    )
    df = df[mask]

df = df[df["match"] >= min_match]
df = df.sort_values(by=["match", "posted"], ascending=[False, False])

# Metrics (small)
st.caption(f"**{len(df)} jobs** • Sorted by best match")

# ====================== CARD VIEW (Main UI) ======================
if len(df) == 0:
    st.info("No jobs match your filters.")
else:
    # 3-column responsive grid
    cols = st.columns(3)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                # Match badge
                match_color = "🟢" if row["match"] >= 90 else "🟠" if row["match"] >= 75 else "🔴"
                st.markdown(
                    f"<div style='text-align: right; font-size: 1.8rem;'>{match_color} **{row['match']}%**</div>",
                    unsafe_allow_html=True
                )
                
                st.subheader(row["title"])
                st.markdown(f"**{row['company']}**")
                st.caption(f"📍 {row['location']}  |  💰 {row['salary']}")
                
                st.divider()
                
                st.markdown("**🛠️ Skills**")
                st.write(row["skills"])
                
                st.caption(f"📅 Posted: {row['posted']}  •  {row['type']}")

# Optional: Reset button in sidebar
with st.sidebar:
    st.header("Controls")
    if st.button("Reset to Sample Data"):
        st.session_state.jobs = pd.DataFrame([
            {"id": str(uuid.uuid4()), "title": "Senior Python Engineer", "company": "TechCorp", "location": "Remote", "salary": "120k–160k", "skills": "Python, Django, AWS, PostgreSQL", "posted": "2026-07-01", "type": "Full-time", "match": 94},
            {"id": str(uuid.uuid4()), "title": "Growth Marketing Manager", "company": "GrowthCo", "location": "New York, NY", "salary": "85k–115k", "skills": "SEO, Content Strategy, Analytics", "posted": "2026-07-02", "type": "Full-time", "match": 87},
            {"id": str(uuid.uuid4()), "title": "Product Designer", "company": "Nexus Studio", "location": "San Francisco", "salary": "130k–170k", "skills": "Figma, User Research, Prototyping", "posted": "2026-07-03", "type": "Full-time", "match": 91}
        ])
        st.rerun()
    
    st.caption("Data lives only during this session.")
