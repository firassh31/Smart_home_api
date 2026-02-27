const API_URL = 'http://127.0.0.1:5000/devices/';

function loadDevices() {
    fetch(API_URL)
        .then(response => response.json())
        .then(devices => {
            const listDiv = document.getElementById('deviceList');
            listDiv.innerHTML = '';
            const activeCount = devices.filter(d => d.status === 'on').length;
            document.getElementById('active-count').textContent = activeCount;

            if (devices.length === 0) {
                listDiv.innerHTML = `
            <div class="empty-state">
            <div class="empty-icon">🏠</div>
            <p>Your home is empty. Tap the <b>+</b> button to add your first device!</p>
            </div>
            `;
                return;
            }

            const devicesByRoom = {};
            devices.forEach(device => {
                const roomName = device.room || 'Unassigned';
                if (!devicesByRoom[roomName]) devicesByRoom[roomName] = [];
                devicesByRoom[roomName].push(device);
            });

            for (const [roomName, roomDevices] of Object.entries(devicesByRoom)) {
                const roomDiv = document.createElement('div');
                roomDiv.className = 'room-container';

                const title = document.createElement('h3');
                title.textContent = roomName;
                roomDiv.appendChild(title);

                roomDevices.forEach(device => {
                    const item = document.createElement('div');
                    item.className = 'device-card';
                    const btnClass = device.status === 'on' ? 'btn-on' : 'btn-off';
                    const btnText = device.status === 'on' ? 'ON' : 'OFF';

                    item.innerHTML = `
                    <div class="device-info">
                        <strong>${device.name}</strong> 
                        <span class="room-label">📍 ${roomName}</span>
                    </div>
                    <div class="device-actions">
                        <button class="toggle-btn ${btnClass}" onclick="toggleDevice('${device.id}', '${device.status}')">${btnText}</button>
                        <button class="delete-btn" onclick="openDeleteModal('${device.id}')">🗑️</button>
                    </div>
                    `;

                    roomDiv.appendChild(item);
                });
                listDiv.appendChild(roomDiv);
            }
        })
        .catch(error => showToast('Error connecting to server', true));
}


function addDevice() {
    const nameInput = document.getElementById('device-name');
    const roomInput = document.getElementById('device-room');

    if (nameInput.value && roomInput.value) {
        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: nameInput.value, room: roomInput.value })
        }).then(response => {
            if (response.ok) {
                nameInput.value = '';
                roomInput.value = '';
                closeAddModal(); // Hides the popup
                loadDevices();   // Refreshes the grid
                showToast("Device added successfully!", false);
            }
        });
    } else {
        showToast("Please enter both a device name and a room", true);
    }
}

function toggleDevice(id, currentStatus) {
    const newStatus = currentStatus === 'on' ? 'off' : 'on';
    fetch(API_URL + id + '/status', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    }).then(response => {
        if (response.ok) loadDevices();
    });
}

// --- Modal Logic ---

// Delete Modal
function openDeleteModal(id) {
    document.getElementById('deleteModal').style.display = 'block';
    document.getElementById('deleteIdField').value = id;
}

function closeModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

function confirmDelete() {
    const id = document.getElementById('deleteIdField').value;
    fetch(API_URL + id, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                closeModal();
                loadDevices();
            } else {
                alert("Error deleting device");
            }
        });
}

// Add Device Modal
function openAddModal() {
    document.getElementById('addModal').style.display = 'block';
}

function closeAddModal() {
    document.getElementById('addModal').style.display = 'none';
}

function showToast(message, isError = false) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');

    // Assigns the 'error' class (Burnt Rust) or 'success' class (Moss Green)
    toast.className = `toast ${isError ? 'error' : 'success'}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Physically removes the toast from the HTML after 3 seconds so they don't pile up invisibly
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
window.onload = loadDevices;