const API_URL = 'http://127.0.0.1:5000/devices/';

function loadDevices() {
    fetch(API_URL)
        .then(response => response.json())
        .then(devices => {
            const listDiv = document.getElementById('deviceList');
            listDiv.innerHTML = '';

            if (devices.length === 0) {
                listDiv.innerHTML = '<p><em>No devices found.</em></p>';
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
                    </div>
                    <div class="device-actions">
                    <button class="toggle-btn ${btnClass}" onclick="toggleDevice('${device.id}', '${device.status}')">${btnText}</button>
        
                    <button class="delete-btn" onclick="openDeleteModal('${device.id}')">Delete 🗑️</button>
                    </div>
                `;

                    roomDiv.appendChild(item);
                });
                listDiv.appendChild(roomDiv);
            }
        })
        .catch(error => console.error('Error:', error));
}

function addDevice() {
    const nameInput = document.getElementById('device-name');
    const roomInput = document.getElementById('device-room');

    if (nameInput.value) {
        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: nameInput.value, room: roomInput.value })
        }).then(response => {
            if (response.ok) {
                nameInput.value = '';
                loadDevices();
            }
        });
    } else {
        alert("Please enter a device name");
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

// Modal Logic
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

window.onload = loadDevices;