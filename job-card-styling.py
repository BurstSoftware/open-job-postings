/* Job Cards */
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

.job-title { 
    font-size: 1.4rem; 
    font-weight: 700; 
    color: #a0c4ff; 
    margin-bottom: 8px; 
}

.company { 
    color: #8f9eff; 
    font-weight: 600; 
}

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

<div class="job-card">
    <div style="display:flex; justify-content:space-between; align-items:start;">
        <div>
            <div class="job-title">{title}</div>
            <div class="company">■ {company}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:1.2rem; font-weight:700; color:#00ff9d;">{salary}</div>
            <div style="color:#8899cc;">{location}</div>
        </div>
    </div>

    <div style="margin: 20px 0 16px 0; display: flex; flex-wrap: wrap; gap: 12px;">
        <span class="badge">{type}</span>
        <span class="badge">Posted {posted}</span>
        <span class="badge">Match: {match}%</span>
    </div>

    <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">
        <strong>Description:</strong> {description}
    </div>
    <div style="color:#b0b8ff; line-height:1.5; margin-bottom:12px;">
        <strong>Requirements:</strong> {requirements}
    </div>
    <div style="color:#b0b8ff; line-height:1.5; margin-bottom:16px;">
        <strong>Benefits:</strong> {benefits}
    </div>

    <div style="display:flex; gap:24px; font-size:0.92rem; color:#8899cc; border-top:1px solid #334477; padding-top:12px;">
        <div><strong>Website:</strong> 
            <a href="{website}" target="_blank" style="color:#6e8cff;">Apply Now</a>
        </div>
        <div><strong>Phone:</strong> {phone}</div>
    </div>
</div>

for _, job in df.iterrows():
    st.html(f"""
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
        <!-- rest of the template above -->
    </div>
    """)

    
