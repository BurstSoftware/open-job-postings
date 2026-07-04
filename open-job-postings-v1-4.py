import streamlit as st
import pandas as pd
import json
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

# ====================== UI ======================
st.title("💼 Job Board Dashboard")
st.markdown("Paste JSON → Add or Replace jobs")

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Jobs", len(st.session_state.jobs))
with col2:
    avg = st.session_state.jobs["match"].mean()
    st.metric("Avg Match", f"{avg:.0f}%")
with col3:
    st.metric("Locations", st.session_state.jobs["location"].nunique())

# Filters
search = st.text_input("🔍 Search title/company/skills", "")
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
df = df[df["match"] >= min_match].sort_values(by=["match", "posted"], ascending=[False, False])

# ====================== JSON IMPORT (FIXED) ======================
with st.expander("📥 Bulk Import / Replace via JSON", expanded=True):
    st.info("Paste a **JSON array** of jobs (or a single object)")
    
    json_input = st.text_area(
        "JSON Input",
        height=220,
        placeholder='''[
  {
    "title": "Senior Data Engineer",
    "company": "DataFlow",
    "location": "Remote",
    "salary": "145k–175k",
    "skills": "Python, Spark, Airflow",
    "posted": "2026-07-04",
    "type": "Full-time",
    "match": 96
  }
]'''
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add to Existing Jobs", type="primary", use_container_width=True):
            if json_input.strip():
                try:
                    raw = json_input.strip()
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        data = [data]
                    if not isinstance(data, list):
                        raise ValueError("Must be array or object")

                    new_rows = []
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        job = item.copy()
                        if "id" not in job or not job["id"]:
                            job["id"] = str(uuid.uuid4())
                        # Fill missing fields
                        for col in st.session_state.jobs.columns:
                            if col not in job:
                                job[col] = "" if col != "match" else 50
                        new_rows.append(job)

                    if new_rows:
                        new_df = pd.DataFrame(new_rows)
                        st.session_state.jobs = pd.concat(
                            [st.session_state.jobs, new_df], ignore_index=True
                        )
                        st.success(f"✅ Added {len(new_rows)} job(s)!")
                        st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    with c2:
        if st.button("🔄 Replace Entire Dataset", use_container_width=True):
            if json_input.strip():
                try:
                    raw = json_input.strip()
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        data = [data]

                    new_rows = []
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        job = item.copy()
                        if "id" not in job or not job["id"]:
                            job["id"] = str(uuid.uuid4())
                        for col in st.session_state.jobs.columns:
                            if col not in job:
                                job[col] = "" if col != "match" else 50
                        new_rows.append(job)

                    if new_rows:
                        st.session_state.jobs = pd.DataFrame(new_rows)
                        st.success(f"✅ Replaced with {len(new_rows)} jobs!")
                        st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ====================== DISPLAY ======================
st.subheader(f"Showing {len(df)} jobs")

tab1, tab2 = st.tabs(["📊 Table View", "🃏 Card View"])

with tab1:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "title": st.column_config.TextColumn("Job Title", width="large"),
            "company": st.column_config.TextColumn("Company"),
            "location": st.column_config.TextColumn("Location"),
            "salary": st.column_config.TextColumn("Salary"),
            "skills": st.column_config.TextColumn("Skills", width="large"),
            "posted": st.column_config.TextColumn("Posted"),
            "type": st.column_config.TextColumn("Type"),
            "match": st.column_config.ProgressColumn(
                "Match Score", min_value=0, max_value=100, format="%d%%"
            ),
        }
    )

with tab2:
    if len(df) == 0:
        st.info("No jobs match your filters.")
    else:
        for _, row in df.iterrows():
            with st.container(border=True):
                cols = st.columns([4, 2])
                with cols[0]:
                    st.subheader(row["title"])
                    st.markdown(f"**{row['company']}** • {row['location']}")
                    st.caption(f"💰 {row['salary']} | {row['type']}")
                    st.write(f"**Skills:** {row['skills']}")
                with cols[1]:
                    st.metric("Match", f"{row['match']}%")
                    st.caption(f"Posted: {row['posted']}")

# Sidebar
with st.sidebar:
    st.header("Actions")
    if st.button("Reset to Sample Data"):
        # Re-create the original 3 jobs
        st.session_state.jobs = pd.DataFrame([
            {"id": str(uuid.uuid4()), "title": "Senior Python Engineer", "company": "TechCorp", "location": "Remote", "salary": "120k–160k", "skills": "Python, Django, AWS, PostgreSQL", "posted": "2026-07-01", "type": "Full-time", "match": 94},
            {"id": str(uuid.uuid4()), "title": "Growth Marketing Manager", "company": "GrowthCo", "location": "New York, NY", "salary": "85k–115k", "skills": "SEO, Content Strategy, Analytics", "posted": "2026-07-02", "type": "Full-time", "match": 87},
            {"id": str(uuid.uuid4()), "title": "Product Designer", "company": "Nexus Studio", "location": "San Francisco", "salary": "130k–170k", "skills": "Figma, User Research, Prototyping", "posted": "2026-07-03", "type": "Full-time", "match": 91}
        ])
        st.rerun()
    
    st.caption("Data is stored only in this session.")
