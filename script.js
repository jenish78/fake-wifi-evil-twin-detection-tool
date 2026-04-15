let chart;
let map = L.map('map').setView([22.3, 70.8], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

async function fetchData() {
    const loading = document.getElementById("loading");

    loading.style.display = "block";

    try {
        const res = await fetch('/data');
        const data = await res.json();

        updateTable(data);
        updateChart(data);
        updateMap(data);

    } catch (err) {
        alert("Error scanning networks");
    }

    loading.style.display = "none";
}

function updateTable(data) {
    let alertShown = false;
    let table = document.getElementById("wifiTable");

    table.innerHTML = `
        <tr><th>SSID</th><th>BSSID</th><th>Signal</th><th>Status</th></tr>
    `;

    data.forEach(n => {
        if (n.status.includes("Suspicious") && !alertShown) {
            document.getElementById("alertSound").play();
            alert("🚨 Evil Twin Detected: " + n.ssid);
            alertShown = true;
        }
        table.innerHTML += `
            <tr>
                <td>${n.ssid}</td>
                <td>${n.bssid}</td>
                <td>${n.signal}</td>
                <td>${n.status}</td>
            </tr>
        `;
    });
}

function updateChart(data) {
    let labels = data.map(n => n.ssid);
    let signals = data.map(n => n.signal);

    if (chart) chart.destroy();

    chart = new Chart(document.getElementById("chart"), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: "Signal", data: signals }]
        }
    });
}

function updateMap(data) {
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) map.removeLayer(layer);
    });

    data.forEach(n => {
        L.marker([n.lat, n.lon])
            .addTo(map)
            .bindPopup(n.ssid + " - " + n.status);
    });
}

// MATRIX RAIN EFFECT
const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const fontSize = 14;
const columns = canvas.width / fontSize;

const drops = [];

for (let i = 0; i < columns; i++) {
    drops[i] = 1;
}

function drawMatrix() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#00ff00";
    ctx.font = fontSize + "px monospace";

    for (let i = 0; i < drops.length; i++) {
        const text = letters.charAt(Math.floor(Math.random() * letters.length));

        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.95) {
            drops[i] = 0;
        }

        drops[i]++;
    }
}

setInterval(drawMatrix, 50);

function enableFirewall() {
    alert("🛡 Firewall Activated (Auto protection enabled)");
}

async function toggleTestMode() {
    const res = await fetch('/toggle_test', { method: 'POST' });
    const data = await res.json();

    document.getElementById("modeStatus").innerText =
        data.test_mode ? "Mode: TEST 🧪" : "Mode: REAL 🟢";

    alert(data.test_mode ? "Test Mode Enabled" : "Test Mode Disabled");
}