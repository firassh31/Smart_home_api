const API_URL = '/devices/';
let activeRoom = 'All', devices = [];

// DOM Helpers (Saves time typing)
const $ = id => document.getElementById(id);
const $$ = selector => document.querySelectorAll(selector);

// Auto-Icon Matcher using clean Regex
const getDeviceIcon = type => {
    switch (type) {
        case 'light': return '💡';
        case 'ac': return '❄️';
        case 'doorlock': return '🔒';
        case 'doorlock': return '🔒';
        default: return '🔌'; // Fallback icon for unknown types
    }
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
        const icon = getDeviceIcon(d.type);
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
const saveDevice = async () => {
    const id = $('editing-device-id').value;
    const name = $('device-name').value;
    const room = $('device-room').value;
    const type = $('device-type').value;

    if (!name || !room) return showToast("Please enter both fields", "error");

    // If we have an ID, we are updating (PUT). Otherwise, adding (POST).
    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}${id}` : API_URL;

    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, room, type })
        });

        if (res.ok) {
            toggleModal('addModal', false);
            loadDevices();
            showToast(`Device ${id ? 'updated' : 'added'} successfully!`, "success");
        } else {
            showToast("Error saving device", "error");
        }
    } catch (e) {
        showToast("Network error", "error");
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
    const deleteBtn = document.querySelector('#deleteModal .danger-btn'); // Disable button to prevent multiple clicks
    if (deleteBtn.disabled) return;
    deleteBtn.disabled = true;
    deleteBtn.innerText = "Deleting...";
    try {
        const res = await fetch(API_URL + $('deleteIdField').value, { method: 'DELETE' });
        if (res.ok) {
            toggleModal('deleteModal', false);
            loadDevices();
            showToast("Device deleted successfully!", "info");
        } else {
            showToast("Error deleting device", "error");
        }
    } catch (error) {
        console.error("Network error:", error);
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerText = "Delete";
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

// Toggle the Sidebar Menu and the Dark Overlay
const toggleSidebar = () => {
    $('sidebar').classList.toggle('show');
    $('sidebar-overlay').classList.toggle('show');
};

const editDevice = (id) => {
    // Find the device data from our local array
    const device = devices.find(d => d.id === id);
    if (!device) return;

    // Pre-fill the modal
    $('modal-title').textContent = 'Edit Device';
    $('editing-device-id').value = device.id;
    $('device-name').value = device.name;
    $('device-room').value = device.room;
    $('device-type').value = device.type;
    // Open modal and close the 3-dot menu
    toggleModal('addModal', true);
    $$('.device-card-dropdown.show').forEach(m => m.classList.remove('show'));
};
// Reusable Modal Logic
const toggleModal = (id, show, fieldId = null) => {
    $(id).style.display = show ? 'block' : 'none';
    if (fieldId) $('deleteIdField').value = fieldId;
};

// Specific Modal Triggers
const openDeleteModal = id => toggleModal('deleteModal', true, id);
const closeModal = () => toggleModal('deleteModal', false);
const openAddModal = () => {
    $('modal-title').textContent = 'Add New Device'; // Reset title
    $('editing-device-id').value = '';               // Clear ID
    $('device-name').value = '';                     // Clear Name
    $('device-room').value = '';                     // Clear Room
    $('device-type').value = '';                     // Clear Type
    toggleModal('addModal', true);                   // Open Modal
};
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