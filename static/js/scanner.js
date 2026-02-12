// API Base URL
const API_BASE = window.location.origin;

// Scanner instance
let html5QrCode = null;
let currentEventId = null;
let recentScans = [];

// Load Events
async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE}/events/`);
        const events = await response.json();

        const select = document.getElementById('scanner-event-select');
        select.innerHTML = '<option value="">Select an event...</option>' +
            events.map(e => `
                <option value="${e.id}">${e.name} - ${new Date(e.event_date).toLocaleDateString()}</option>
            `).join('');

        select.addEventListener('change', () => {
            currentEventId = parseInt(select.value);
        });

        // Auto-select first event
        if (events.length > 0) {
            select.value = events[0].id;
            currentEventId = events[0].id;
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

// Start Scanner
async function startScanner() {
    if (!currentEventId) {
        alert('Please select an event first!');
        return;
    }

    try {
        html5QrCode = new Html5Qrcode("qr-reader");

        await html5QrCode.start(
            { facingMode: "environment" },
            {
                fps: 10,
                qrbox: { width: 250, height: 250 }
            },
            onScanSuccess,
            onScanFailure
        );

        document.getElementById('start-scanner-btn').style.display = 'none';
        document.getElementById('stop-scanner-btn').style.display = 'inline-block';

    } catch (err) {
        console.error('Error starting scanner:', err);
        alert('Failed to start scanner. Please check camera permissions.');
    }
}

// Stop Scanner
async function stopScanner() {
    if (html5QrCode) {
        try {
            await html5QrCode.stop();
            html5QrCode = null;

            document.getElementById('start-scanner-btn').style.display = 'inline-block';
            document.getElementById('stop-scanner-btn').style.display = 'none';
        } catch (err) {
            console.error('Error stopping scanner:', err);
        }
    }
}

// On Scan Success
async function onScanSuccess(decodedText, decodedResult) {
    // Stop scanner temporarily to prevent multiple scans
    if (html5QrCode) {
        await html5QrCode.pause();
    }

    // Extract ticket ID from QR code
    const ticketId = decodedText.trim();

    // Check-in via API
    try {
        const response = await fetch(`${API_BASE}/checkin/qr?ticket_id=${encodeURIComponent(ticketId)}&event_id=${currentEventId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            showResult(result, 'success');
            addRecentScan({
                success: true,
                name: result.participant_name,
                email: result.email,
                time: new Date()
            });
        } else {
            showResult(result.detail, 'error');
            addRecentScan({
                success: false,
                message: result.detail.message || result.detail,
                time: new Date()
            });
        }
    } catch (error) {
        showResult({ message: `Error: ${error.message}` }, 'error');
        addRecentScan({
            success: false,
            message: error.message,
            time: new Date()
        });
    }

    // Resume scanner after 2 seconds
    setTimeout(() => {
        if (html5QrCode) {
            html5QrCode.resume();
        }
    }, 2000);
}

// On Scan Failure (silent)
function onScanFailure(error) {
    // Silent - scanning continuously
}

// Show Result
function showResult(result, type) {
    const resultDiv = document.getElementById('scan-result');

    if (type === 'success') {
        resultDiv.innerHTML = `
            <h3>✅ Check-in Successful!</h3>
            <div class="participant-info">
                <div class="info-row">
                    <span class="info-label">Name:</span>
                    <span class="info-value">${result.participant_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span class="info-value">${result.email}</span>
                </div>
                ${result.college ? `
                <div class="info-row">
                    <span class="info-label">College:</span>
                    <span class="info-value">${result.college}</span>
                </div>
                ` : ''}
                <div class="info-row">
                    <span class="info-label">Event:</span>
                    <span class="info-value">${result.event_name}</span>
                </div>
            </div>
        `;
        resultDiv.className = 'result-display success show';

        // Play success sound (optional)
        playSound('success');

    } else {
        resultDiv.innerHTML = `
            <h3>❌ Check-in Failed</h3>
            <p>${result.message || 'Unknown error occurred'}</p>
            ${result.reason ? `<p><small>Reason: ${result.reason}</small></p>` : ''}
        `;
        resultDiv.className = 'result-display error show';

        // Play error sound (optional)
        playSound('error');
    }

    // Hide after 5 seconds
    setTimeout(() => {
        resultDiv.classList.remove('show');
    }, 5000);
}

// Add to Recent Scans
function addRecentScan(scan) {
    recentScans.unshift(scan);
    if (recentScans.length > 10) {
        recentScans.pop();
    }
    updateRecentScansList();
}

// Update Recent Scans List
function updateRecentScansList() {
    const listDiv = document.getElementById('recent-scans-list');

    if (recentScans.length === 0) {
        listDiv.innerHTML = '<p>No scans yet</p>';
        return;
    }

    const html = recentScans.map(scan => {
        const timeStr = scan.time.toLocaleTimeString();

        if (scan.success) {
            return `
                <div class="scan-item">
                    <div class="name">✅ ${scan.name}</div>
                    <div class="time">${timeStr} - ${scan.email}</div>
                </div>
            `;
        } else {
            return `
                <div class="scan-item error">
                    <div class="name">❌ Failed</div>
                    <div class="time">${timeStr} - ${scan.message}</div>
                </div>
            `;
        }
    }).join('');

    listDiv.innerHTML = html;
}

// Play Sound (optional - implement if needed)
function playSound(type) {
    // You can add audio elements and play them here
    // For now, using browser beep
    if (type === 'success') {
        // Success sound
    } else {
        // Error sound
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadEvents();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (html5QrCode) {
        html5QrCode.stop();
    }
});