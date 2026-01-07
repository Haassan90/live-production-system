/***********************
 * BACKEND CONFIG
 ***********************/
const API_BASE = "http://127.0.0.1:8000/api";
let ws;

function connectWebSocket() {
    ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
        console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "tick") {
            loadDashboard(); // re-fetch from backend
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected, retrying...");
        setTimeout(connectWebSocket, 2000);
    };
}
/***********************
 * USERS (TEMP LOGIN)
 * (Later ERPNext auth se replace hoga)
 ***********************/
const users = [
    { username: "1111", password: "1111", location: "Modan" },
    { username: "2222", password: "2222", location: "Baldeya" },
    { username: "3333", password: "3333", location: "Al-Khraj" },
    { username: "Admin", password: "12345", location: "all" }
];

let currentUser = null;

/***********************
 * LOCATIONS
 ***********************/
const locations = ["Modan", "Baldeya", "Al-Khraj"];

/***********************
 * PIPE SPEED (sec/m)
 * (Temporary – backend me move hoga)
 ***********************/
const pipeSpeed = {
    "20": 20,
    "32": 20,
    "33": 20,
    "110": 52
};

/***********************
 * MACHINE STATE
 * (Temporary – backend replace karega)
 ***********************/
let machinesData = {};

/***********************
 * INIT MACHINES
 * 12 machines per location
 ***********************/
locations.forEach((loc, i) => {
    machinesData[loc] = Array.from({ length: 12 }, (_, idx) => ({
        id: i * 1000 + idx + 1,
        name: `Machine ${idx + 1}`,
        status: "free",   // free | running | stopped
        job: null,
        timer: null
    }));
});

/***********************
 * LOGIN
 ***********************/
document.getElementById("login-form").addEventListener("submit", e => {
    e.preventDefault();

    const u = username.value.trim();
    const p = password.value.trim();

    const user = users.find(x => x.username === u && x.password === p);
    if (!user) {
        alert("Invalid username or password");
        return;
    }

    currentUser = user;

    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("dashboard-section").classList.remove("hidden");
loadMachinesFromBackend();
    showDashboard();
    startLivePolling();
});

/***********************
 * DASHBOARD
 ***********************/
function showDashboard() {
    const container = document.getElementById("locations");
    container.innerHTML = "";

    const visibleLocations =
        currentUser.location === "all"
            ? locations
            : [currentUser.location];

    visibleLocations.forEach(renderLocation);
}
function loadDashboard() {
    fetch(`http://127.0.0.1:8000/api/dashboard?token=${TOKEN}`)
        .then(res => res.json())
        .then(data => {
            renderDashboard(data);
        });
}

function renderLocation(location) {
    const div = document.createElement("div");
    div.className = "location-card";
    div.innerHTML = `
        <h2>${location}</h2>
        <div class="machines-grid" id="grid-${location}"></div>
    `;
    document.getElementById("locations").appendChild(div);
    renderMachines(location);
}

/***********************
 * RENDER MACHINES
 ***********************/
function renderMachines(location) {
    const grid = document.getElementById(`grid-${location}`);
    grid.innerHTML = "";

    machinesData[location].forEach(machine => {
        const card = document.createElement("div");
        card.className = "machine-card";

        card.innerHTML = `
            <h3>${machine.name}</h3>
            <p>Status: <b>${machine.status.toUpperCase()}</b></p>

            ${
                machine.job
                ? `
                <div class="job-card">
                    <p><b>JOB CARD</b></p>
                    <p>Work Order: ${machine.job.work_order}</p>
                    <p>Pipe Size: ${machine.job.size} mm</p>
                    <p>Quantity: ${machine.job.completed_qty.toFixed(1)}
                        / ${machine.job.total_qty} m</p>
                    <p>ETA Remaining: ${machine.job.remaining_time}</p>
                </div>
                `
                : `<p>No Job Assigned</p>`
            }
        `;
        grid.appendChild(card);
    });
}

/***********************
 * PRODUCTION SIMULATION
 * (TEMP – backend me move hoga)
 ***********************/
function runMachine(location, id) {
    const machine = machinesData[location].find(m => m.id === id);
    if (!machine || machine.status !== "running") return;

    const speed = pipeSpeed[machine.job.size];
    machine.job.completed_qty += (1 / speed);

    const remainingQty =
        machine.job.total_qty - machine.job.completed_qty;
    const remainingSec = remainingQty * speed;

    const h = Math.floor(remainingSec / 3600);
    const m = Math.floor((remainingSec % 3600) / 60);
    machine.job.remaining_time = `${h}h ${m}m`;

    if (machine.job.completed_qty >= machine.job.total_qty) {
        clearInterval(machine.timer);
        machine.timer = null;
        machine.status = "free";
        machine.job = null;
    }

    renderMachines(location);
}

/***********************
 * TEMP AUTO START DEMO
 * (REMOVE when backend is live)
 ***********************/
function demoAssignJob() {
    locations.forEach(loc => {
        const machine = machinesData[loc][0];
        if (!machine.job) {
            const qty = 500;
            const size = "110";
            const speed = pipeSpeed[size];
            const totalSec = qty * speed;

            machine.job = {
                work_order: "WO-DEMO",
                size,
                total_qty: qty,
                completed_qty: 0,
                remaining_time: `${Math.floor(totalSec / 3600)}h ${Math.floor((totalSec % 3600) / 60)}m`
            };
            machine.status = "running";
            machine.timer = setInterval(() => runMachine(loc, machine.id), 1000);
        }
    });
}

/* COMMENT THIS OUT WHEN BACKEND CONNECTS */
// demoAssignJob();
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    connectWebSocket();
});
async function loadMachinesFromBackend() {
    try {
        const res = await fetch(`${API_BASE}/machines`);
        const data = await res.json();

        machinesData = data; // backend structure same hai
        showDashboard();
    } catch (err) {
        console.error("Backend not reachable", err);
    }
}
// runMachine()
// demoAssignJob()
/***********************
 * LIVE POLLING (STEP 13)
 ***********************/
let pollingInterval = null;

function startLivePolling() {
    if (pollingInterval) return;

    pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/machines`);
            const data = await res.json();
            machinesData = data;
            showDashboard();
        } catch (err) {
            console.error("Polling failed", err);
        }
    }, 5000); // every 5 sec
}

