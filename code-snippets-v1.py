CATEGORIES = {
    "All Categories": "All",
    "Tech": "💻 Tech",
    "Business": "📊 Business",
    "Trade": "🔧 Trade & Skilled",
    "Creative": "🎨 Creative",
    "Healthcare": "🩺 Healthcare",
    "Sales": "💼 Sales",
    "Education": "📚 Education",
    "Other": "🔀 Other"
}

location = st.selectbox(
        "■ Location", 
        ["All United States", "Remote", 
         "New York, NY", "San Francisco, CA", "Chicago, IL", 
         "Los Angeles, CA", "Austin, TX", "Seattle, WA", 
         "Boston, MA", "Denver, CO", "Atlanta, GA"]
    )

