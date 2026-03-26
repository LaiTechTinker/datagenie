// Data Genie Frontend - Vanilla JS Logic & API Integration

// Configuration
const API_BASE = 'http://localhost:5000';
let currentDatasetId = null;
let datasetInfo = null;
let data = {}; // Global data store for cleaning/profiling


// DOM Elements
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const navLinks = document.querySelectorAll('.nav-link');
const pageSections = document.querySelectorAll('.page-section');
const toggleBtn = document.getElementById('toggle-sidebar');
const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const uploadBtn = document.getElementById('upload-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const toastContainer = document.getElementById('toast-container');

// Chat elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendChatBtn = document.getElementById('send-chat');
const mlChat = document.getElementById('ml-chat');
const mlInput = document.getElementById('ml-input');
const sendMlBtn = document.getElementById('send-ml');

// Section buttons
const profileBtn = document.getElementById('profile-btn');
const cleaningBtn = document.getElementById('cleaning-btn');
const vizBtn = document.getElementById('viz-btn');
const mlBtn = document.getElementById('ml-btn');
const generateProfileBtn = document.getElementById('generate-profile');
const analyzeIssuesBtn = document.getElementById('analyze-issues');
const exportCsvBtn = document.getElementById('export-csv');
const exportReportBtn = document.getElementById('export-report');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initUpload();
    initResponsive();
    initSectionButtons();
    loadDatasetInfo();
});

// Navigation
function initNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            switchSection(targetId);
        });
    });
}

function switchSection(sectionId) {
    // Update nav active state
    navLinks.forEach(link => link.classList.remove('active'));
    document.querySelector(`a[href="#${sectionId}"]`).classList.add('active');
    
    // Switch sections
    pageSections.forEach(section => section.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    
    // Add main-content class for mobile
    if (window.innerWidth <= 768) {
        mainContent.classList.add('mobile-main');
    }
}

// Responsive sidebar
function initResponsive() {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        sidebar.classList.toggle('collapsed');
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('collapsed', 'open');
        } else {
            sidebar.classList.add('collapsed');
        }
    });
}

// File Upload
function initUpload() {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = `Selected: ${file.name}`;
            uploadBtn.disabled = false;
        }
    });

    uploadBtn.addEventListener('click', uploadFile);
}

async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) return;

    showLoading('Uploading dataset...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`Upload failed: ${response.status}`);

        const data = await response.json();
        currentDatasetId = data.file_id;
        localStorage.setItem('datasetId', currentDatasetId);
        
        hideLoading();
        showToast('Dataset uploaded successfully!', 'success');
        switchSection('dashboard');
        loadDatasetInfo();
    } catch (error) {
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Load dataset info on dashboard
function loadDatasetInfo() {
    currentDatasetId = localStorage.getItem('datasetId');
    if (!currentDatasetId) return;

    // Simulate fetching info or call /summary API
    fetch(`${API_BASE}/summary`,{
        method: 'POST',
             headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ file_id: currentDatasetId })

    })
        .then(res => res.json())
        .then(data => {
            datasetInfo = data;
            document.getElementById('rows-count').textContent = data.rows || 'N/A';
            document.getElementById('cols-count').textContent = data.columns || 'N/A';
            populateColumns(data.columns_list || []);
        })
        .catch(() => {
            // Fallback mock data
            document.getElementById('rows-count').textContent = '1,234';
            document.getElementById('cols-count').textContent = '12';
            populateColumns(['age', 'income', 'city', 'sales']);
        });
}

function populateColumns(columns) {
    const list = document.getElementById('columns-list');
    list.innerHTML = '';
    columns.forEach(col => {
        const li = document.createElement('li');
        li.textContent = col;
        list.appendChild(li);
    });
}

// Section buttons
function initSectionButtons() {
    profileBtn?.addEventListener('click', () => switchSection('profile'));
    cleaningBtn?.addEventListener('click', () => switchSection('cleaning'));
    vizBtn?.addEventListener('click', () => switchSection('visualize'));
    mlBtn?.addEventListener('click', () => switchSection('ml'));

    generateProfileBtn.addEventListener('click', generateProfile);
    analyzeIssuesBtn.addEventListener('click', analyzeCleaning);
    sendChatBtn.addEventListener('click', sendVizQuery);
    sendMlBtn.addEventListener('click', sendMlQuery);
    chatInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendVizQuery());
    mlInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMlQuery());
    exportCsvBtn.addEventListener('click', exportCsv);
    exportReportBtn.addEventListener('click', exportReport);
}

// Data Profiling
async function generateProfile() {
    if (!currentDatasetId) return showToast('Please upload a dataset first', 'error');
    
    showLoading('Generating profile...');
    
    try {
        const response = await fetch(`${API_BASE}/profiling`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId})
        });
        const result = await response.json();
        const data = result.profile;
        // console.log('Profiling data:', data);
        
        // Update overview
        document.getElementById('prof-rows').textContent = data.shape[0].toLocaleString();
        document.getElementById('prof-cols').textContent = data.shape[1];
        let tm = Object.values(data.missing_values).reduce((a,b)=>a+b,0);
        document.getElementById('prof-missing').textContent = tm;
        document.getElementById('prof-missing-label').textContent = tm===0 ? 'Perfect Data' : 'Total Missing';
        
        // AI Insights (from result.insights)
        let aiInsights = result.insights || 'No AI insights available.';
        document.getElementById('ai-insights').textContent = aiInsights;
        
        // Populate dashboard
        renderProfColumns(data);
        renderProfColSelect(data);
        renderProfInsights(data);
        renderProfCats(data);
        renderProfCorr(data);
        
        hideLoading();
        showToast('Profile generated!', 'success');
    } catch (error) {
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
    }
}

function renderProfColumns(data) {
    let tb = document.querySelector('#prof-columnsTable tbody');
    tb.innerHTML = '';
    data.columns.forEach(c=>{
        let r = tb.insertRow();
        r.innerHTML = `<td onclick="selProfCol('${c}')">${c}</td><td>${data.dtypes[c]}</td><td>${data.unique_values[c]}</td><td>${data.missing_values[c]}</td>`;
    });
}

function renderProfColSelect(data) {
    let s = document.getElementById('prof-colSelect');
    s.innerHTML = '<option value="">Select...</option>';
    data.columns.forEach(c=>{
        let o = document.createElement('option');
        o.value = c;
        o.textContent = c;
        s.appendChild(o);
    });
    s.onchange = showProfStats;
}

function showProfStats() {
    let c = document.getElementById('prof-colSelect').value;
    let cont = document.getElementById('prof-stats');
    if (!c) { cont.innerHTML = ''; return; }
    let st = p.summary_stats[c];
    cont.innerHTML = `<div class="stats-container" style="gap:20px;">
        <div class="stat-item"><div class="stat-label">Mean</div><div class="stat-value">${fmtProf(st.mean)}</div></div>
        <div class="stat-item"><div class="stat-label">Std</div><div class="stat-value">${fmtProf(st.std)}</div></div>
        <div class="stat-item"><div class="stat-label">Min</div><div class="stat-value">${fmtProf(st.min)}</div></div>
        <div class="stat-item"><div class="stat-label">Max</div><div class="stat-value">${fmtProf(st.max)}</div></div>
        <div class="stat-item"><div class="stat-label">Median</div><div class="stat-value">${fmtProf(st['50%'])}</div></div>
    </div>`;
}

function fmtProf(v) { return v===''||v===null||v===undefined ? 'N/A' : (typeof v==='number' ? (Number.isInteger(v)?v:v.toFixed(2)) : v); }

function selProfCol(c) { document.getElementById('prof-colSelect').value = c; showProfStats(); }

function renderProfInsights(data) {
    let cont = document.getElementById('prof-insights'), html = '';
    let tm = Object.values(data.missing_values).reduce((a,b)=>a+b,0);
    if (tm===0) html += '<span class="insight-badge badge-good">✅ No missing values</span>';
    data.columns.forEach(c=>{
        let up = (data.unique_values[c]/data.shape[0])*100;
        if (up>10) html += `<span class="insight-badge badge-warning">⚠️ High cardinality: ${c}</span>`;
    });
    cont.innerHTML = html || '<p style="color:#27ae60;">Dataset looks clean!</p>';
}

function renderProfCats(data) {
    let cont = document.getElementById('prof-cats');
    cont.innerHTML = '';
    data.columns.forEach(c=>{
        let st = data.summary_stats[c];
        if (st.freq && st.top) {
            let card = document.createElement('div'); 
            card.className = 'card';
            card.style.padding = '20px';
            card.innerHTML = `<h4 style="margin-bottom:15px;">${c}</h4>
                <div class="stat-item" style="margin-bottom:10px;"><div class="stat-label">Top</div><div class="stat-value">${st.top}</div></div>
                <div class="stat-item" style="margin-bottom:10px;"><div class="stat-label">Freq</div><div class="stat-value">${st.freq}</div></div>
                <div class="stat-item"><div class="stat-label">Unique</div><div class="stat-value">${data.unique_values[c]}</div></div>`;
            cont.appendChild(card);
        }
    });
}

function renderProfCorr(data) {
    let thead = document.querySelector('#prof-corrTable thead tr'), tbody = document.querySelector('#prof-corrTable tbody');
    let nc = data.columns.filter(c=>['int64','float64'].includes(data.dtypes[c]));
    thead.innerHTML = '<th></th>'+nc.map(c=>`<th>${c}</th>`).join('');
    tbody.innerHTML = '';
    nc.forEach(r=>{
        let row = tbody.insertRow();
        row.innerHTML = `<td style="font-weight:600;">${r}</td>`;
        nc.forEach(col=>{
            let cv = data.correlation[r]?.[col] || 0;
            let cell = row.insertCell();
            cell.className = 'corr-cell';
            cell.textContent = cv.toFixed(2);
            let av = Math.abs(cv);
            if (av>=0.7) cell.classList.add('corr-strong');
            else if (av>=0.4) cell.classList.add('corr-medium');
            else if (av>=0.2) cell.classList.add('corr-weak');
        });
    });
}

// Copy insights
document.getElementById('copy-insights')?.addEventListener('click', ()=>{
    let text = document.getElementById('ai-insights').textContent;
    navigator.clipboard.writeText(text).then(()=>showToast('Copied to clipboard!', 'success'));
});


const mockProfileData = () => ({
    summary_stats: {
        'Rows': 1234,
        'Columns': 12,
        'Missing %': '2.3%',
        'Duplicates': 5
    }
});

// Cleaning
async function analyzeCleaning() {
    if (!currentDatasetId) return showToast('Please upload a dataset first', 'error');
    
    showLoading('Analyzing data quality...');
    
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId})
        });
        const result = await response.json();
        renderCleaningDashboard(result.table, result.explanation);
        hideLoading();
        showToast('Analysis complete!', 'success');
    } catch (error) {
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
        renderCleaningDemo();
    }
}

function renderCleaningDashboard(table, explanation) {
    data.cleanTable = table; // Global for actions
    
    // Update metrics
    let totalIssues = table.length;
    let missing = table.filter(r=>r.issue_type==='missing_values').length;
    let dups = table.filter(r=>r.issue_type==='duplicates').length;
    let outs = table.filter(r=>r.issue_type==='outliers').length;
    
    document.getElementById('clean-total-issues').textContent = totalIssues;
    document.getElementById('clean-missing-count').textContent = missing;
    document.getElementById('clean-duplicates').textContent = dups;
    document.getElementById('clean-outliers').textContent = outs;
    
    // AI explanation
    document.getElementById('clean-ai-explain').textContent = explanation || 'No AI advice available.';
    
    // Issues table
    let tbody = document.querySelector('#clean-issues-table tbody');
    tbody.innerHTML = '';
    table.forEach((row, idx)=>{
        let r = tbody.insertRow();
        r.innerHTML = `
            <td><i class="fas fa-${getIssueIcon(row.issue_type)}"></i> ${row.issue_type.replace('_',' ').toUpperCase()}</td>
            <td>${row.column === 'ALL' ? '<strong>All Rows</strong>' : row.column}</td>
            <td><strong>${row.count}</strong></td>
            <td>${row.percentage ? row.percentage + '%' : '-'}</td>
            <td>${row.suggestion}</td>
            <td>
                <select onchange="setCleanAction(${idx},this.value)" style="padding:5px;border-radius:4px;">
                    <option value="">Choose...</option>
                    ${getActionsForIssue(row.issue_type).map(a=>`<option value="${a}">${a}</option>`).join('')}
                </select>
            </td>
        `;
    });
    
    updateCleanSummary();
}

function getIssueIcon(type) {
    if (type==='missing_values') return 'minus-square';
    if (type==='duplicates') return 'copy';
    if (type==='outliers') return 'chart-line';
    return 'exclamation-triangle';
}

function getActionsForIssue(type) {
    if (type==='missing_values') return ['fill_median', 'fill_mean', 'fill_mode', 'drop'];
    if (type==='duplicates') return ['remove'];
    if (type==='outliers') return ['remove', 'cap'];
    return [];
}

function setCleanAction(idx, action) {
    if (!data.cleanTable) return;
    data.cleanTable[idx].selected_action = action;
    updateCleanSummary();
}

function updateCleanSummary() {
    let selected = data.cleanTable?.filter(r=>r.selected_action).length || 0;
    document.getElementById('clean-actions-summary').innerHTML = 
        selected === 0 ? 'No actions selected' :
        `<i class="fas fa-check-circle" style="color:#27ae60;"></i> ${selected} actions ready. <button onclick="applySelectedActions()" style="background:#27ae60;color:white;border:none;padding:8px 16px;border-radius:6px;margin-left:10px;cursor:pointer;"><i class="fas fa-play"></i> Apply All</button>`;
}

async function applyAllAutoFixes() {
    if (!data.cleanTable) return showToast('No analysis available', 'error');
    let actions = data.cleanTable.map(r=>({
        type: r.issue_type,
        column: r.column,
        action: r.selected_action || getDefaultAction(r.issue_type)
    })).filter(a=>a.action);
    
    showLoading('Applying fixes...');
    try {
        const response = await fetch(`${API_BASE}/clean`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId, actions})
        });
        if (response.ok) {
            showToast('Data cleaned & downloaded!', 'success');
            // Trigger download handled by backend
        }
    } catch (error) {
        showToast('Error applying fixes', 'error');
    }
    hideLoading();
}

function getDefaultAction(type) {
    if (type==='missing_values') return 'fill_median';
    if (type==='duplicates') return 'remove';
    if (type==='outliers') return 'cap';
    return '';
}

async function applySelectedActions() {
    if (!data.cleanTable) return;
    let actions = data.cleanTable.filter(r=>r.selected_action).map(r=>({
        type: r.issue_type,
        column: r.column,
        action: r.selected_action
    }));
    
    if (actions.length === 0) return showToast('Select actions first', 'warning');
    
    showLoading('Cleaning data...');
    try {
        const response = await fetch(`${API_BASE}/clean`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId, actions})
        });
        if (response.ok) {
            const blob = await response.blob();
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = 'cleaned_data.csv';
            a.click();
            showToast('Cleaned data downloaded!', 'success');
        }
    } catch (error) {
        showToast('Cleaning failed', 'error');
    }
    hideLoading();
}

function downloadCleanedData() {
    showToast('Ready for download after applying fixes', 'info');
}

function renderCleaningDemo() {
    let demoTable = [
        {issue_type: 'missing_values', column: 'age', count: 45, percentage: 3.4, suggestion: 'fill with median'},
        {issue_type: 'duplicates', column: 'ALL', count: 12, suggestion: 'remove duplicate rows'},
        {issue_type: 'outliers', column: 'charges', count: 23, suggestion: 'consider capping outliers'}
    ];
    renderCleaningDashboard(demoTable, 'Demo data - upload file to analyze your dataset.');
}


function displayCleaningSuggestions(suggestions) {
    const container = document.getElementById('cleaning-suggestions');
    container.innerHTML = suggestions.map(s => `
        <div class="suggestion-card ${s.type}">
            <h4>${s.title}</h4>
            <p>${s.description}</p>
            <div class="suggestion-actions">
                <button onclick="applyCleaning('${s.id}')">Apply</button>
                <button onclick="ignoreCleaning('${s.id}')">Ignore</button>
            </div>
        </div>
    `).join('');
}

const mockCleaningSuggestions = () => [
    {id:1, title:'Missing values in Age', description:'23% missing. Recommend imputation.', type:'warning'},
    {id:2, title:'Duplicate rows', description:'15 duplicates found.', type:'warning'},
    {id:3, title:'Outliers in Sales', description:'Extreme values detected.', type:'danger'}
];

// Visualization Chat
let vizHistory = [];

// Load dataset columns for viz
async function loadVizColumns() {
    if (!currentDatasetId) return showToast('Upload dataset first', 'warning');
    document.getElementById('load-columns-btn').textContent = 'Loading...';
    try {
        const response = await fetch(`${API_BASE}/profiling`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId})
        });
        const result = await response.json();
        data.vizColumns = result.profile.columns;
        showToast(`${data.vizColumns.length} columns loaded!`, 'success');
    } catch (error) {
        showToast('Error loading columns', 'error');
    }
    document.getElementById('load-columns-btn').innerHTML = '<i class="fas fa-sync"></i> Load Columns';
}

async function generateVizChart() {
    const query = document.getElementById('viz-query-input').value.trim();
    if (!query || !currentDatasetId) return showToast('Need dataset & query', 'warning');
    
    addVizMessage('user', query);
    document.getElementById('viz-query-input').value = '';
    
    showLoading('Generating chart...');
    
    try {
        const response = await fetch(`${API_BASE}/visualize`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id: currentDatasetId, query})
        });
        
        if (!response.ok) throw new Error('API error');
        
        const result = await response.json();
        addVizChart(result.spec, result.chart);
        vizHistory.unshift({query, spec: result.spec, html: result.chart});
        if (vizHistory.length > 10) vizHistory = vizHistory.slice(0,10);
        updateVizGallery();
        showToast('Chart generated!', 'success');
    } catch (error) {
        addVizMessage('ai', `Error: ${error.message}. Try "bar chart age vs charges"`, true);
        showToast('Generation failed', 'error');
    }
    hideLoading();
}

function addVizMessage(sender, text, isError = false) {
    const container = document.getElementById('viz-chat-messages');
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerHTML = `<div class="message-bubble ${isError ? 'error-bg' : ''}">${text}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function addVizChart(spec, chartHtml) {
    const container = document.getElementById('viz-chat-messages');
    const div = document.createElement('div');
    div.className = 'message ai';
    div.innerHTML = `
        <div class="message-bubble">
            <strong>${spec.chart_type?.toUpperCase()} Chart</strong><br>
            ${spec.x_column} ${spec.y_column ? 'vs ' + spec.y_column : ''} 
            ${spec.aggregation ? `(${spec.aggregation})` : ''}
            <div class="chart-container" id="viz-${Date.now()}"></div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    
    // Inject Plotly HTML
    const chartId = div.querySelector('.chart-container').id;
    div.querySelector('.chart-container').outerHTML = chartHtml;
}

function updateVizGallery() {
    const container = document.getElementById('viz-recent-charts');
    container.innerHTML = vizHistory.map((h, i) => `
        <div class="chart-thumb" onclick="regenerateViz(${i})" style="cursor:pointer;">
            <div style="padding:20px; background:#f8f9fa; border-radius:12px;">
                <strong style="font-size:1.1rem;">${h.query.substring(0,40)}${h.query.length>40?'...':''}</strong>
                <div style="font-size:0.9rem; color:#666; margin-top:8px;">
                    ${h.spec.chart_type} • ${h.spec.x_column}${h.spec.y_column ? ' vs ' + h.spec.y_column : ''}
                </div>
            </div>
        </div>
    `).join('') || '<p style="grid-column:1/-1; text-align:center; color:#999;">No charts yet</p>';
}

function regenerateViz(index) {
    const item = vizHistory[index];
    document.getElementById('viz-query-input').value = item.query;
    generateVizChart();
}

function clearVizChat() {
    document.getElementById('viz-chat-messages').innerHTML = '';
    vizHistory = [];
    updateVizGallery();
    showToast('Cleared!', 'success');
}

// Enter support
document.getElementById('viz-query-input').addEventListener('keypress', e => {
    if (e.key === 'Enter') generateVizChart();
});


function addChatMessage(sender, text, chartUrl = null) {
    const messages = sender === 'user' ? chatMessages : mlChat;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${text}
            ${chartUrl ? `<img src="${chartUrl}" class="chart-img" alt="Chart">` : ''}
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// ML
async function sendMlQuery() {
    const query = mlInput.value.trim();
    if (!query) return;

    addMlMessage('user', query);
    mlInput.value = '';

    showLoading('Training models...');
    
    try {
        const response = await fetch(`${API_BASE}/ml`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query, dataset_id: currentDatasetId})
        });
        const data = await response.json();
        displayMlResults(data);
        hideLoading();
    } catch (error) {
        displayMlResults(mockMlResults());
        hideLoading();
    }
}

function addMlMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-bubble">${text}</div>`;
    mlChat.appendChild(messageDiv);
    mlChat.scrollTop = mlChat.scrollHeight;
}

function displayMlResults(data) {
    document.getElementById('ml-results').innerHTML = `
        <div class="summary-card">
            <h3>${data.best_model || 'Random Forest'}</h3>
            <p>Accuracy: ${(data.accuracy * 100 || 92.3).toFixed(1)}%</p>
        </div>
        <table>
            <thead><tr><th>Model</th><th>Accuracy</th></tr></thead>
            <tbody>${data.model_comparison?.map(m => `<tr><td>${m.model}</td><td>${(m.acc*100).toFixed(1)}%</td></tr>`).join('') || ''}</tbody>
        </table>
    `;
}

const mockMlResults = () => ({
    best_model: 'Random Forest',
    accuracy: 0.923,
    model_comparison: [
        {model: 'Random Forest', acc: 0.923},
        {model: 'XGBoost', acc: 0.912},
        {model: 'Logistic', acc: 0.887}
    ]
});

// Export
async function exportCsv() {
    if (!currentDatasetId) return showToast('No dataset to export', 'error');
    
    window.open(`${API_BASE}/export/csv?dataset_id=${currentDatasetId}`);
}

async function exportReport() {
    if (!currentDatasetId) return showToast('No dataset to export', 'error');
    
    window.open(`${API_BASE}/export/report?dataset_id=${currentDatasetId}`);
}

// Cleaning actions
function applyCleaning(id) {
    showToast('Cleaning applied!', 'success');
    // API call would go here
}

function ignoreCleaning(id) {
    showToast('Suggestion ignored', 'success');
}

// Loading & Toast utilities
function showLoading(text) {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
