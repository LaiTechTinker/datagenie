// Data Genie Frontend - Vanilla JS Logic & API Integration

// Configuration
const API_BASE = 'http://localhost:5000';
let currentDatasetId = null;
let datasetInfo = null;

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
    // const currentDatasetId=localStorage.getItem('datasetId')
    if (!currentDatasetId) return showToast('Please upload a dataset first', 'error');
    
    showLoading('Generating profile...');
    
    try {
        const response = await fetch(`${API_BASE}/profiling`, {
            method: 'POST',
              headers: {
        'Content-Type': 'application/json'
    },
   body: JSON.stringify({ file_id: currentDatasetId })
        });
        const data = await response.json();
        console.log(data)
        displayProfileResults(data);
        hideLoading();
        showToast('Profile generated!', 'success');
    } catch (error) {
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
        return {}
        // displayProfileResults(mockProfileData());
    }
}

function displayProfileResults(data) {
    const container = document.getElementById('profile-results');
    container.innerHTML = `
        <table>
            <thead>
                <tr><th>Metric</th><th>Value</th></tr>
            </thead>
            <tbody>
                ${Object.entries(data.profile || {}).map(([key, val]) => 
                    `<tr><td>${key}</td><td>${val}</td></tr>`
                ).join('')}
            </tbody>
        </table>
    `;
}

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
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ file_id: currentDatasetId })
})
        const suggestions = await response.json();
        displayCleaningSuggestions(suggestions);
        hideLoading();
    } catch (error) {
        hideLoading();
        displayCleaningSuggestions(mockCleaningSuggestions());
        showToast('Using demo suggestions', 'success');
    }
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
async function sendVizQuery() {
    const query = chatInput.value.trim();
    if (!query) return;

    addChatMessage('user', query);
    chatInput.value = '';

    showLoading('Creating visualization...');
    
    try {
        const response = await fetch(`${API_BASE}/visualize`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query, dataset_id: currentDatasetId})
        });
        const data = await response.json();
        addChatMessage('ai', data.response || 'Chart created!', data.chart_url || null);
        hideLoading();
    } catch (error) {
        addChatMessage('ai', 'Error creating chart. Demo chart shown.', '/demo-chart.png');
        hideLoading();
    }
}

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
