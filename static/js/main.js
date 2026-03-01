const API_URL = 'http://127.0.0.1:5000/devices/';
let activeRoom = 'All', devices = [];

// DOM Helpers (Saves time typing)
const $ = id => document.getElementById(id);
const $$ = selector => document.querySelectorAll(selector);

// Auto-Icon Matcher using clean Regex
const getDeviceIcon = name => {
    const n = name.toLowerCase();
    if (n.match(/tv|screen|television/)) return '📺';
    if (n.match(/lamp|light|bulb/)) return '💡';
    if (n.match(/ac|air|condition/)) return '❄️';
    if (n.match(/music|speaker|audio/)) return '🎵';
    if (n.match(/fan/)) return '🎐';
    return '';
};

// --- 1. Fetch & Render ---
const loadDevices = async () => {
    try {
        const res = await fetch(API_URL);
        devices = await res.json();
        renderUI();
    } catch {
        showToast('Error connecting to server', 'error');
    }
};

const renderUI = () => {
    // Render Navigation Pills
    const rooms = ['All', ...new Set(devices.map(d => d.room || 'Unassigned'))];
    $('room-nav').innerHTML = rooms.map(r =>
        `<button class="room-pill ${r === activeRoom ? 'active' : ''}" onclick="activeRoom='${r}'; renderUI()">${r}</button>`
    ).join('');

    // Filter Devices & Update Active Badge
    const filtered = activeRoom === 'All' ? devices : devices.filter(d => (d.room || 'Unassigned') === activeRoom);
    $('active-count').textContent = filtered.filter(d => d.status === 'on').length;

    // Handle Empty State
    if (!filtered.length) {
        $('deviceList').innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-icon">🏠</div>
                <p>No devices found here.</p>
            </div>`;
        return;
    }

    // Render Device Grid
    $('deviceList').innerHTML = filtered.map(d => {
        const icon = getDeviceIcon(d.name);
        return `
        <div class="device-card">
            <div class="device-card-menu">
                <button class="device-card-menu-btn" onclick="toggleDeviceMenu('device-menu-${d.id}')">⋮</button>
                <div id="device-menu-${d.id}" class="device-card-dropdown">
                    <button onclick="editDevice('${d.id}')">✏️ Edit</button>
                    <button class="delete-text" onclick="openDeleteModal('${d.id}')">🗑️ Delete</button>
                </div>
            </div>
            
            <div class="device-info">
                <div class="device-title">
                    ${icon ? `<div class="device-icon">${icon}</div>` : ''}               
                    <strong>${d.name}</strong> 
                </div>
                <span class="room-label">📍 ${d.room || 'Unassigned'}</span>
            </div>
            
            <div class="device-actions">
                <button class="toggle-btn ${d.status === 'on' ? 'btn-on' : 'btn-off'}" onclick="toggleDevice('${d.id}', '${d.status}')">${d.status === 'on' ? 'ON' : 'OFF'}</button>            
            </div>
        </div>`;
    }).join('');
};

// --- 2. Device Actions (API Calls) ---
const addDevice = async () => {
    const name = $('device-name').value, room = $('device-room').value;
    if (!name || !room) return showToast("Please enter both fields", "error");

    const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, room })
    });

    if (res.ok) {
        $('device-name').value = '';
        $('device-room').value = '';
        toggleModal('addModal', false);
        loadDevices();
        showToast("Device added successfully!", "success");
    }
};

const toggleDevice = async (id, status) => {
    const res = await fetch(`${API_URL}${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: status === 'on' ? 'off' : 'on' })
    });
    if (res.ok) loadDevices();
};

const confirmDelete = async () => {
    const res = await fetch(API_URL + $('deleteIdField').value, { method: 'DELETE' });
    if (res.ok) {
        toggleModal('deleteModal', false);
        loadDevices();
        showToast("Device deleted successfully!", "info");
    } else {
        showToast("Error deleting device", "error");
    }
};

// --- 3. UI, Menus & Modals ---
const toggleDeviceMenu = id => {
    $$('.device-card-dropdown.show').forEach(m => m.id !== id && m.classList.remove('show'));
    $(id).classList.toggle('show');
};

// Close menus when clicking outside
document.addEventListener('click', e => {
    if (!e.target.matches('.device-card-menu-btn')) {
        $$('.device-card-dropdown.show').forEach(m => m.classList.remove('show'));
    }
});

const editDevice = () => showToast("Edit feature coming soon!", "info");

// Reusable Modal Logic
const toggleModal = (id, show, fieldId = null) => {
    $(id).style.display = show ? 'block' : 'none';
    if (fieldId) $('deleteIdField').value = fieldId;
};

// Specific Modal Triggers
const openDeleteModal = id => toggleModal('deleteModal', true, id);
const closeModal = () => toggleModal('deleteModal', false);
const openAddModal = () => toggleModal('addModal', true);
const closeAddModal = () => toggleModal('addModal', false);

// Toast Notifications
const showToast = (msg, type = 'success') => {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    $('toast-container').appendChild(t);
    setTimeout(() => t.remove(), 3000);
};

// Initialize app
window.onload = loadDevices;