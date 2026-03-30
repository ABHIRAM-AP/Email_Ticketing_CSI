// API Base URL
const API_BASE = window.location.origin;

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');

    // Load data for specific tabs
    if (tabName === 'checkin') {
        loadEventStats();
    } else if (tabName === 'csv-upload') {
        loadCSVStats();
    }
}

// CSV Upload
document.getElementById('csv-upload-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];

    if (!file) {
        showUploadResult('Please select a CSV file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showUploadResult('Uploading and processing CSV...', 'info');

        const response = await fetch(`${API_BASE}/csv/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            let message = `✅ Upload Complete!\n\n`;
            message += `Total rows: ${result.total_rows}\n`;
            message += `✔ Imported: ${result.imported}\n`;
            message += `⚠ Duplicates: ${result.duplicates}\n`;
            message += `❌ Errors: ${result.errors}`;

            if (result.error_details && result.error_details.length > 0) {
                message += `\n\nFirst few errors:\n` + result.error_details.join('\n');
            }

            showUploadResult(message, result.errors > 0 ? 'info' : 'success');
            fileInput.value = '';
            loadCSVStats();
        } else {
            showUploadResult(`Error: ${result.detail}`, 'error');
        }
    } catch (error) {
        showUploadResult(`Upload failed: ${error.message}`, 'error');
    }
});

function showUploadResult(message, type) {
    const resultBox = document.getElementById('upload-result');
    resultBox.textContent = message;
    resultBox.className = `result-box ${type}`;
    resultBox.style.display = 'block';
}

// Load CSV Statistics
async function loadCSVStats() {
    try {
        const response = await fetch(`${API_BASE}/csv/stats`);
        const stats = await response.json();

        document.getElementById('participants-stats').innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_participants}</div>
                <div class="stat-label">Total Hackathon Participants</div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading CSV stats:', error);
    }
}

// Load Participants List
async function loadParticipants() {
    try {
        const response = await fetch(`${API_BASE}/csv/participants`);
        const participants = await response.json();

        const listHtml = participants.map(p => `
            <div class="participant-item">
                <div>
                    <div class="name">${p.name}</div>
                    <div class="email">${p.email}</div>
                </div>
                <div>${p.college || '-'}</div>
            </div>
        `).join('');

        document.getElementById('participants-list').innerHTML = listHtml || '<p>No participants imported yet.</p>';
    } catch (error) {
        console.error('Error loading participants:', error);
    }
}

// Load Event Statistics for the Hackathon
async function loadEventStats() {
    try {
        const response = await fetch(`${API_BASE}/checkin/stats`);
        const stats = await response.json();

        // Update stat cards
        const statCards = document.querySelectorAll('#event-stats .stat-card');
        statCards[0].querySelector('.stat-number').textContent = stats.total_registrations;
        statCards[1].querySelector('.stat-number').textContent = stats.checked_in_registrations;
        statCards[2].querySelector('.stat-number').textContent = stats.csv_checkins;
        statCards[3].querySelector('.stat-number').textContent = stats.remaining_capacity;

        // Load recent check-ins
        loadRecentCheckins();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Check-in by Email
async function checkInByEmail(e) {
    e.preventDefault();

    const email = document.getElementById('checkin-email').value;
    const resultDiv = document.getElementById('email-checkin-result');

    try {
        resultDiv.innerHTML = '<div class="result-box info">Processing...</div>';

        const response = await fetch(`${API_BASE}/checkin/email?email=${encodeURIComponent(email)}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h4>✅ ${result.message}</h4>
                    <p><strong>Name:</strong> ${result.participant_name}</p>
                    <p><strong>Email:</strong> ${result.email}</p>
                    ${result.college ? `<p><strong>College:</strong> ${result.college}</p>` : ''}
                </div>
            `;
            document.getElementById('checkin-email').value = '';
            loadEventStats();
        } else {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <h4>❌ Check-in Failed</h4>
                    <p>${result.detail.message || result.detail}</p>
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="result-box error">Error: ${error.message}</div>`;
    }
}

// Load Recent Check-ins
async function loadRecentCheckins() {
    try {
        const response = await fetch(`${API_BASE}/checkin/recent?limit=10`);
        const checkins = await response.json();

        const listHtml = checkins.map(c => {
            const time = new Date(c.checked_in_at).toLocaleTimeString();
            const source = c.source === 'qr' ? '🎫 QR' : '📧 Email';

            return `
                <div class="checkin-item">
                    <div class="info">
                        <div class="name">${c.email}</div>
                        <div class="time">${time}</div>
                    </div>
                    <div class="badge">${source}</div>
                </div>
            `;
        }).join('');

        document.getElementById('recent-checkins-list').innerHTML = listHtml || '<p>No check-ins yet.</p>';
    } catch (error) {
        console.error('Error loading recent check-ins:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadCSVStats();
});