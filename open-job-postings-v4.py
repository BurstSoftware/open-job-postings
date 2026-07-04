<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💼 Job Board • Streamlit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Space+Grotesk:wght@500;600&amp;display=swap');
        
        :root {
            --primary: #6366f1;
        }
        
        body {
            font-family: 'Inter', system_ui, sans-serif;
        }
        
        .font-display {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-weight: 600;
        }

        .job-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .job-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }

        .match-bar {
            height: 8px;
            background: linear-gradient(to right, #6366f1, #a5b4fc);
            border-radius: 9999px;
            transition: width 0.5s ease;
        }

        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1f2937;
        }

        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        .metric-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .json-textarea {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.875rem;
            line-height: 1.5;
        }

        .beautiful-table {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
</head>
<body class="bg-zinc-950 text-zinc-200">
    <div class="max-w-screen-xl mx-auto px-6 py-8">
        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-x-4">
                <div class="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center">
                    <i class="fa-solid fa-briefcase text-white text-3xl"></i>
                </div>
                <div>
                    <h1 class="text-4xl font-display font-semibold tracking-tight">Job Board</h1>
                    <p class="text-zinc-400 text-sm">Beautiful dashboard • JSON import ready</p>
                </div>
            </div>
            
            <div class="flex items-center gap-x-3">
                <button onclick="exportToJSON()" 
                        class="flex items-center gap-x-2 px-4 py-2.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 rounded-2xl text-sm font-medium transition-colors">
                    <i class="fa-solid fa-download mr-2"></i>
                    <span>Export JSON</span>
                </button>
                <button onclick="resetToSample()" 
                        class="flex items-center gap-x-2 px-4 py-2.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 rounded-2xl text-sm font-medium transition-colors">
                    <i class="fa-solid fa-undo mr-2"></i>
                    <span>Reset Sample</span>
                </button>
            </div>
        </div>

        <!-- Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8" id="metrics">
            <!-- Populated by JS -->
        </div>

        <!-- Controls -->
        <div class="flex flex-col lg:flex-row gap-4 mb-6">
            <!-- Search -->
            <div class="flex-1">
                <div class="relative">
                    <i class="fa-solid fa-search absolute left-4 top-3.5 text-zinc-400"></i>
                    <input type="text" id="search-input" 
                           class="w-full bg-zinc-900 border border-zinc-700 focus:border-indigo-500 rounded-3xl pl-11 pr-4 py-3 text-sm placeholder:text-zinc-400"
                           placeholder="Search by title, company or skills...">
                </div>
            </div>
            
            <!-- Min Match -->
            <div class="w-full lg:w-72">
                <div class="flex items-center gap-x-3 bg-zinc-900 border border-zinc-700 rounded-3xl px-4 py-2">
                    <div class="text-sm text-zinc-400 whitespace-nowrap">Min Match</div>
                    <input type="range" id="min-match" min="0" max="100" step="5" value="0" 
                           class="flex-1 accent-indigo-500">
                    <div id="min-match-value" class="font-mono text-sm w-8 text-right">0</div>
                </div>
            </div>
        </div>

        <!-- JSON Import Section -->
        <div class="mb-8 bg-zinc-900 border border-zinc-700 rounded-3xl p-6">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="font-semibold flex items-center gap-x-2">
                        <i class="fa-solid fa-file-import text-indigo-400"></i>
                        <span>Bulk Import via JSON</span>
                    </h3>
                    <p class="text-xs text-zinc-400 mt-0.5">Paste an array of job objects. New jobs will be added.</p>
                </div>
                <div class="flex gap-x-2">
                    <button onclick="addFromJSON()" 
                            class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 transition-colors text-white text-sm font-semibold rounded-2xl flex items-center gap-x-2">
                        <i class="fa-solid fa-plus"></i>
                        <span>Add Jobs</span>
                    </button>
                    <button onclick="replaceFromJSON()" 
                            class="px-5 py-2 bg-zinc-700 hover:bg-zinc-600 transition-colors text-sm font-semibold rounded-2xl flex items-center gap-x-2">
                        <i class="fa-solid fa-sync"></i>
                        <span>Replace All</span>
                    </button>
                </div>
            </div>
            
            <textarea id="json-input" rows="6" 
                      class="json-textarea w-full bg-zinc-950 border border-zinc-700 rounded-2xl p-4 text-sm font-mono resize-y focus:outline-none focus:border-indigo-500"
                      placeholder='[
  {
    "title": "Senior Data Engineer",
    "company": "DataFlow Inc",
    "location": "Remote",
    "salary": "145k–175k",
    "skills": "Python, Spark, Airflow, AWS",
    "posted": "2026-07-04",
    "type": "Full-time",
    "match": 96
  }
]'></textarea>
        </div>

        <!-- Tabs -->
        <div class="mb-4 flex border-b border-zinc-700">
            <button onclick="switchTab(0)" id="tab-0"
                    class="tab-button active px-6 py-3 font-semibold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-x-2">
                <i class="fa-solid fa-table"></i>
                <span>Table View</span>
            </button>
            <button onclick="switchTab(1)" id="tab-1"
                    class="tab-button px-6 py-3 font-semibold text-zinc-400 hover:text-zinc-200 flex items-center gap-x-2">
                <i class="fa-solid fa-th-large"></i>
                <span>Card View</span>
            </button>
        </div>

        <!-- Table View -->
        <div id="table-view" class="tab-content">
            <div class="beautiful-table bg-zinc-900 border border-zinc-700 rounded-3xl overflow-hidden">
                <table class="w-full">
                    <thead>
                        <tr class="bg-zinc-800 text-left text-xs uppercase tracking-wider text-zinc-400">
                            <th class="px-6 py-4 font-medium">Job Title</th>
                            <th class="px-6 py-4 font-medium">Company</th>
                            <th class="px-6 py-4 font-medium">Location</th>
                            <th class="px-6 py-4 font-medium">Salary</th>
                            <th class="px-6 py-4 font-medium">Skills</th>
                            <th class="px-6 py-4 font-medium text-center">Posted</th>
                            <th class="px-6 py-4 font-medium text-center">Type</th>
                            <th class="px-6 py-4 font-medium text-center w-32">Match</th>
                        </tr>
                    </thead>
                    <tbody id="table-body" class="divide-y divide-zinc-700 text-sm">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Card View -->
        <div id="card-view" class="tab-content hidden">
            <div id="card-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                <!-- Populated by JS -->
            </div>
        </div>

        <div class="mt-4 text-xs text-zinc-500 flex justify-between items-center">
            <div id="results-count"></div>
            <div class="flex items-center gap-x-1.5">
                <i class="fa-solid fa-info-circle"></i>
                <span>Data stored in browser (session)</span>
            </div>
        </div>
    </div>

    <script>
        // ==================== DATA ====================
        let jobs = [
            {
                id: crypto.randomUUID(),
                title: "Senior Python Engineer",
                company: "TechCorp",
                location: "Remote",
                salary: "120k–160k",
                skills: "Python, Django, AWS, PostgreSQL",
                posted: "2026-07-01",
                type: "Full-time",
                match: 94
            },
            {
                id: crypto.randomUUID(),
                title: "Growth Marketing Manager",
                company: "GrowthCo",
                location: "New York, NY",
                salary: "85k–115k",
                skills: "SEO, Content Strategy, Analytics",
                posted: "2026-07-02",
                type: "Full-time",
                match: 87
            },
            {
                id: crypto.randomUUID(),
                title: "Product Designer",
                company: "Nexus Studio",
                location: "San Francisco",
                salary: "130k–170k",
                skills: "Figma, User Research, Prototyping",
                posted: "2026-07-03",
                type: "Full-time",
                match: 91
            }
        ];

        // Load from localStorage if exists
        function loadFromStorage() {
            const saved = localStorage.getItem('jobBoardData');
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        jobs = parsed;
                    }
                } catch (e) {}
            }
        }

        function saveToStorage() {
            localStorage.setItem('jobBoardData', JSON.stringify(jobs));
        }

        // ==================== RENDERING ====================
        function updateMetrics(filteredJobs) {
            const container = document.getElementById('metrics');
            const total = filteredJobs.length;
            const avgMatch = total > 0 
                ? Math.round(filteredJobs.reduce((sum, j) => sum + j.match, 0) / total) 
                : 0;
            const uniqueLocations = new Set(filteredJobs.map(j => j.location)).size;

            container.innerHTML = `
                <div class="metric-card border border-zinc-700 p-5 rounded-3xl">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="text-zinc-400 text-xs tracking-widest">TOTAL JOBS</div>
                            <div class="text-4xl font-semibold mt-1">${total}</div>
                        </div>
                        <i class="fa-solid fa-briefcase text-3xl text-indigo-400/70"></i>
                    </div>
                </div>
                <div class="metric-card border border-zinc-700 p-5 rounded-3xl">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="text-zinc-400 text-xs tracking-widest">AVG MATCH</div>
                            <div class="text-4xl font-semibold mt-1">${avgMatch}<span class="text-2xl text-zinc-400">%</span></div>
                        </div>
                        <i class="fa-solid fa-chart-line text-3xl text-emerald-400/70"></i>
                    </div>
                </div>
                <div class="metric-card border border-zinc-700 p-5 rounded-3xl">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="text-zinc-400 text-xs tracking-widest">LOCATIONS</div>
                            <div class="text-4xl font-semibold mt-1">${uniqueLocations}</div>
                        </div>
                        <i class="fa-solid fa-globe text-3xl text-amber-400/70"></i>
                    </div>
                </div>
            `;
        }

        function renderTable(filteredJobs) {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            if (filteredJobs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="px-6 py-12 text-center text-zinc-400">
                            <i class="fa-solid fa-search text-2xl mb-3 block"></i>
                            No jobs found matching your filters.
                        </td>
                    </tr>
                `;
                return;
            }

            filteredJobs.forEach(job => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-zinc-800/50 transition-colors';
                
                const matchColor = job.match >= 90 ? 'text-emerald-400' : 
                                  job.match >= 75 ? 'text-amber-400' : 'text-orange-400';
                
                row.innerHTML = `
                    <td class="px-6 py-4 font-medium">${job.title}</td>
                    <td class="px-6 py-4 text-zinc-300">${job.company}</td>
                    <td class="px-6 py-4 text-zinc-300">${job.location}</td>
                    <td class="px-6 py-4 font-mono text-sm text-zinc-300">${job.salary}</td>
                    <td class="px-6 py-4 text-xs text-zinc-400 max-w-[220px] truncate">${job.skills}</td>
                    <td class="px-6 py-4 text-center text-xs text-zinc-400">${job.posted}</td>
                    <td class="px-6 py-4 text-center">
                        <span class="inline-block px-3 py-1 text-xs rounded-full bg-zinc-800 text-zinc-300">${job.type}</span>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center justify-center gap-x-2">
                            <div class="w-16 bg-zinc-700 rounded-full h-2">
                                <div class="match-bar h-2 rounded-full" style="width: ${job.match}%"></div>
                            </div>
                            <span class="font-mono text-xs font-semibold w-8 text-right ${matchColor}">${job.match}</span>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }

        function renderCards(filteredJobs) {
            const container = document.getElementById('card-container');
            container.innerHTML = '';

            if (filteredJobs.length === 0) {
                container.innerHTML = `
                    <div class="col-span-full text-center py-12 text-zinc-400">
                        <i class="fa-solid fa-search text-4xl mb-4"></i>
                        <p>No jobs match your current filters.</p>
                    </div>
                `;
                return;
            }

            filteredJobs.forEach(job => {
                const matchColor = job.match >= 90 ? '#10b981' : 
                                  job.match >= 75 ? '#f59e0b' : '#f97316';
                
                const card = document.createElement('div');
                card.className = `job-card bg-zinc-900 border border-zinc-700 rounded-3xl p-5 flex flex-col`;
                
                card.innerHTML = `
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="font-semibold text-xl leading-tight">${job.title}</h3>
                            <div class="flex items-center gap-x-2 mt-1">
                                <span class="font-medium text-zinc-300">${job.company}</span>
                            </div>
                        </div>
                        
                        <div class="text-right">
                            <div class="text-xs text-zinc-400">Match</div>
                            <div class="text-3xl font-semibold" style="color: ${matchColor}">${job.match}</div>
                            <div class="text-[10px] text-zinc-400 -mt-1">/ 100</div>
                        </div>
                    </div>

                    <div class="flex-1">
                        <div class="flex items-center gap-x-2 text-sm mb-3">
                            <i class="fa-solid fa-map-marker-alt text-zinc-400 w-4"></i>
                            <span class="text-zinc-300">${job.location}</span>
                        </div>
                        
                        <div class="flex items-center gap-x-2 text-sm mb-3">
                            <i class="fa-solid fa-money-bill-wave text-zinc-400 w-4"></i>
                            <span class="font-mono text-emerald-300">${job.salary}</span>
                        </div>

                        <div class="mb-4">
                            <div class="text-xs text-zinc-400 mb-1.5">Required Skills</div>
                            <div class="text-sm text-zinc-300 leading-snug">${job.skills}</div>
                        </div>
                    </div>

                    <div class="flex items-center justify-between pt-4 border-t border-zinc-700 text-xs">
                        <div>
                            <span class="px-3 py-1 rounded-2xl bg-zinc-800 text-zinc-300">${job.type}</span>
                        </div>
                        <div class="text-zinc-400">
                            <i class="fa-regular fa-calendar mr-1"></i>
                            ${job.posted}
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function updateResultsCount(count) {
            document.getElementById('results-count').innerHTML = 
                `<span class="font-medium">${count}</span> job${count !== 1 ? 's' : ''} shown`;
        }

        function filterAndRender() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
            const minMatch = parseInt(document.getElementById('min-match').value);

            let filtered = jobs.filter(job => {
                const matchesSearch = !searchTerm || 
                    job.title.toLowerCase().includes(searchTerm) ||
                    job.company.toLowerCase().includes(searchTerm) ||
                    job.skills.toLowerCase().includes(searchTerm);
                
                const matchesMatch = job.match >= minMatch;
                
                return matchesSearch && matchesMatch;
            });

            // Sort by match descending
            filtered.sort((a, b) => b.match - a.match);

            // Update UI
            updateMetrics(filtered);
            renderTable(filtered);
            renderCards(filtered);
            updateResultsCount(filtered.length);
        }

        // ==================== JSON HANDLING ====================
        function parseJSONInput() {
            const textarea = document.getElementById('json-input');
            const raw = textarea.value.trim();
            
            if (!raw) {
                alert("Please paste some JSON first.");
                return null;
            }

            try {
                let data = JSON.parse(raw);
                
                if (!Array.isArray(data)) {
                    data = [data];
                }
                
                return data;
            } catch (e) {
                alert("Invalid JSON format. Please check your input.");
                return null;
            }
        }

        function addFromJSON() {
            const data = parseJSONInput();
            if (!data) return;

            let added = 0;
            
            data.forEach(item => {
                if (!item || typeof item !== 'object') return;
                
                const newJob = {
                    id: item.id || crypto.randomUUID(),
                    title: item.title || "Untitled Position",
                    company: item.company || "Unknown Company",
                    location: item.location || "Remote",
                    salary: item.salary || "Not specified",
                    skills: item.skills || "",
                    posted: item.posted || new Date().toISOString().split('T')[0],
                    type: item.type || "Full-time",
                    match: parseInt(item.match) || 50
                };
                
                jobs.push(newJob);
                added++;
            });

            if (added > 0) {
                saveToStorage();
                filterAndRender();
                document.getElementById('json-input').value = '';
                alert(`✅ Successfully added ${added} job(s)!`);
            }
        }

        function replaceFromJSON() {
            const data = parseJSONInput();
            if (!data) return;

            if (!confirm(`This will replace all ${jobs.length} current jobs with the new data. Continue?`)) {
                return;
            }

            const newJobs = [];
            
            data.forEach(item => {
                if (!item || typeof item !== 'object') return;
                
                newJobs.push({
                    id: item.id || crypto.randomUUID(),
                    title: item.title || "Untitled Position",
                    company: item.company || "Unknown Company",
                    location: item.location || "Remote",
                    salary: item.salary || "Not specified",
                    skills: item.skills || "",
                    posted: item.posted || new Date().toISOString().split('T')[0],
                    type: item.type || "Full-time",
                    match: parseInt(item.match) || 50
                });
            });

            if (newJobs.length > 0) {
                jobs = newJobs;
                saveToStorage();
                filterAndRender();
                document.getElementById('json-input').value = '';
                alert(`✅ Dataset replaced with ${newJobs.length} job(s)!`);
            }
        }

        function exportToJSON() {
            const dataStr = JSON.stringify(jobs, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = 'jobs_export.json';
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        }

        function resetToSample() {
            if (!confirm("Reset to original sample data?")) return;
            
            jobs = [
                {
                    id: crypto.randomUUID(),
                    title: "Senior Python Engineer",
                    company: "TechCorp",
                    location: "Remote",
                    salary: "120k–160k",
                    skills: "Python, Django, AWS, PostgreSQL",
                    posted: "2026-07-01",
                    type: "Full-time",
                    match: 94
                },
                {
                    id: crypto.randomUUID(),
                    title: "Growth Marketing Manager",
                    company: "GrowthCo",
                    location: "New York, NY",
                    salary: "85k–115k",
                    skills: "SEO, Content Strategy, Analytics",
                    posted: "2026-07-02",
                    type: "Full-time",
                    match: 87
                },
                {
                    id: crypto.randomUUID(),
                    title: "Product Designer",
                    company: "Nexus Studio",
                    location: "San Francisco",
                    salary: "130k–170k",
                    skills: "Figma, User Research, Prototyping",
                    posted: "2026-07-03",
                    type: "Full-time",
                    match: 91
                }
            ];
            
            localStorage.removeItem('jobBoardData');
            filterAndRender();
        }

        // ==================== TABS ====================
        let currentTab = 0;

        function switchTab(tabIndex) {
            const tableView = document.getElementById('table-view');
            const cardView = document.getElementById('card-view');
            const tab0 = document.getElementById('tab-0');
            const tab1 = document.getElementById('tab-1');

            if (tabIndex === 0) {
                tableView.classList.remove('hidden');
                cardView.classList.add('hidden');
                tab0.classList.add('active', 'border-b-2', 'border-indigo-500', 'text-indigo-400');
                tab1.classList.remove('active', 'border-b-2', 'border-indigo-500', 'text-indigo-400');
                tab1.classList.add('text-zinc-400');
            } else {
                tableView.classList.add('hidden');
                cardView.classList.remove('hidden');
                tab1.classList.add('active', 'border-b-2', 'border-indigo-500', 'text-indigo-400');
                tab0.classList.remove('active', 'border-b-2', 'border-indigo-500', 'text-indigo-400');
                tab0.classList.add('text-zinc-400');
            }
            currentTab = tabIndex;
        }

        // ==================== EVENT LISTENERS ====================
        function setupEventListeners() {
            // Search
            document.getElementById('search-input').addEventListener('input', filterAndRender);
            
            // Min match slider
            const slider = document.getElementById('min-match');
            const valueDisplay = document.getElementById('min-match-value');
            
            slider.addEventListener('input', () => {
                valueDisplay.textContent = slider.value;
                filterAndRender();
            });
            
            // Initial value
            valueDisplay.textContent = slider.value;
        }

        // ==================== INITIALIZATION ====================
        function initialize() {
            loadFromStorage();
            
            // Set initial slider value
            document.getElementById('min-match').value = 0;
            document.getElementById('min-match-value').textContent = '0';
            
            setupEventListeners();
            
            // Initial render
            filterAndRender();
            
            // Show table view by default
            document.getElementById('table-view').classList.remove('hidden');
            document.getElementById('card-view').classList.add('hidden');
            
            // Make tab buttons nicer
            const tab0 = document.getElementById('tab-0');
            tab0.classList.add('active', 'border-b-2', 'border-indigo-500', 'text-indigo-400');
        }

        // Boot the app
        window.onload = initialize;
    </script>
</body>
</html>
