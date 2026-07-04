import streamlit as st
import pandas as pd
import json
import uuid

st.set_page_config(page_title="Job Board", page_icon="💼", layout="wide")

# Initialize data
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

st.title("💼 Job Board Dashboard")
st.markdown("Paste JSON to add/replace jobs • Beautiful table + card views")

# === Metrics ===
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Jobs", len(st.session_state.jobs))
with col2:
    avg_match = st.session_state.jobs["match"].mean()
    st.metric("Avg Match Score", f"{avg_match:.0f}%")
with col3:
    st.metric("Unique Locations", st.session_state.jobs["location"].nunique())

# === Filters ===
search = st.text_input("🔍 Search (title, company, skills)", "")
min_match = st.slider("Minimum Match %", 0, 100, 0)

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

# === JSON Import ===
with st.expander("📥 Bulk Import / Replace via JSON", expanded=False):
    st.info("Paste a JSON array of job objects below")
    json_input = st.text_area(
        "JSON",
        height=200,
        placeholder='''[
  {
    "title": "New Role",
    "company": "Example",
    "location": "Remote",
    "salary": "100k–140k",
    "skills": "Python, SQL",
    "posted": "2026-07-04",
    "type": "Full-time",
    "match": 88
  }
]'''
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add to existing jobs", type="primary"):
            if json_input.strip():
                try:
                    data = json.loads(json_input)
                    if isinstance(data, dict):
                        data = [data]
                    new_rows = []
                    for item in data:
                        if isinstance(item, dict):
                            job = item.copy()
                            if "id" not in job:
                                job["id"] = str(uuid.uuid4())
                            # Fill missing columns
                            for col in st.session_state.jobs.columns:
                                if col not in job:
                                    job[col] = "" if col != "match" else 50
                            new_rows.append(job)
                    
                    if new_rows:
                        new_df = pd.DataFrame(new_rows)
                        st.session_state.jobs = pd.concat(
                            [st.session_state.jobs, new_df], ignore_index=True
                        )
                        st.success(f"Added {len(new_rows)} jobs!")
                        st.rerun()
                except Exception as e:
                    st.error(f"JSON Error: {e}")

    with c2:
        if st.button("🔄 Replace entire dataset"):
            if json_input.strip():
                try:
                    data = json.loads(json_input)
                    if isinstance(data, dict):
                        data = [data]
                    new_rows = []
                    for item in data:
                        if isinstance(item, dict):
                            job = item.copy()
                            if "id" not in job:
                                job["id"] = str(uuid.uuid4())
                            for col in st.session_state.jobs.columns:
                                if col not in job:
                                    job[col] = "" if col != "match" else 50
                            new_rows.append(job)
                    
                    if new_rows:
                        st.session_state.jobs = pd.DataFrame(new_rows)
                        st.success(f"Dataset replaced with {len(new_rows)} jobs!")
                        st.rerun()
                except Exception as e:
                    st.error(f"JSON Error: {e}")

# === Display ===
st.subheader(f"Showing {len(df)} jobs")

tab1, tab2 = st.tabs(["📊 Table View", "🃏 Card View"])

with tab1:
    # Beautiful styled dataframe
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
                "Match Score",
                min_value=0,
                max_value=100,
                format="%d%%"
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
                    st.metric("Match", f"{row['match']}%", help="How well this matches you")
                    st.caption(f"Posted: {row['posted']}")

# Sidebar extras
with st.sidebar:
    st.header("Actions")
    if st.button("Reset to Sample Data"):
        # Reinitialize
        st.session_state.jobs = pd.DataFrame([...])  # same as initial data above
        st.rerun()
    
    st.caption("Data lives only in this session (refreshes clear it)")
