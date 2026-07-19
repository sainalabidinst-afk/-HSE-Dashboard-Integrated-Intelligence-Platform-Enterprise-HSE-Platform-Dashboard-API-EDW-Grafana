/**
 * Safety Observations Module
 */

const ObservationModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('observations', {
            init: initView
        });
    }

    async function initView(view) {
        currentPage = 1;
        if (view === 'dashboard') {
            await loadDashboard();
        } else if (view === 'list') {
            await loadList();
        }
    }

    async function loadDashboard() {
        showLoading('observation-dashboard-content');
        try {
            const data = await HSEApp.get('/api/observations/dashboard');
            if (data) renderObservationDashboard(data);
        } catch (error) {
            console.error('Failed to load observation dashboard:', error);
            showToast('Failed to load observation dashboard', 'error');
        }
    }

    function renderObservationDashboard(data) {
        const container = document.getElementById('observation-dashboard-content');
        if (!container) return;

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi b"><div class="label">Total Observations</div><div class="val">${data.total_observations || 0}</div><div class="dot b"></div></div>
                <div class="card kpi g"><div class="label">Safe Acts</div><div class="val">${data.safe_observations || 0}</div><div class="dot g"></div></div>
                <div class="card kpi r"><div class="label">Unsafe Acts</div><div class="val">${data.unsafe_observations || 0}</div><div class="dot r"></div></div>
                <div class="card kpi a"><div class="label">Open Items</div><div class="val">${data.open_items || 0}</div><div class="dot a"></div></div>
            </div>
            <div class="grid2">
                <div class="card"><div class="title">By Type</div><canvas id="observation-type-chart"></canvas></div>
                <div class="card"><div class="title">By Status</div><canvas id="observation-status-chart"></canvas></div>
            </div>
        `;

        setTimeout(() => {
            initObservationCharts(data);
        }, 100);
    }

    function initObservationCharts(data) {
        const typeChart = document.getElementById('observation-type-chart');
        if (typeChart) {
            new Chart(typeChart, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.by_type || {}),
                    datasets: [{
                        data: Object.values(data.by_type || {}),
                        backgroundColor: ['#4caf50', '#f44336', '#2196f3']
                    }]
                },
                options: { responsive: true }
            });
        }

        const statusChart = document.getElementById('observation-status-chart');
        if (statusChart) {
            new Chart(statusChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.by_status || {}),
                    datasets: [{
                        label: 'Observations',
                        data: Object.values(data.by_status || {}),
                        backgroundColor: '#2196f3'
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }

    async function loadList() {
        showLoading('observation-list-content');
        try {
            const data = await HSEApp.get(`/api/observations/list?page=${currentPage}&page_size=20`);
            if (data) renderObservationList(data);
        } catch (error) {
            console.error('Failed to load observations:', error);
            showToast('Failed to load observations', 'error');
        }
    }

    function renderObservationList(data) {
        const container = document.getElementById('observation-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.observation_id}</td>
                <td>${HSEApp.formatDate(item.observation_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.observation_type || '-'}</td>
                <td>${item.category || '-'}</td>
                <td><span class="pill ${item.status === 'Closed' ? 'g' : item.status === 'Open' ? 'a' : 'gray'}">${item.status}</span></td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('observations', 'add')">+ New Observation</button>
                <button class="btn btn-secondary" onclick="ObservationModule.refreshList()">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Date</th><th>Site</th><th>Type</th><th>Category</th><th>Status</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    }

    function refreshList() {
        loadList();
    }

    return { initStatic, init: initView };
})();
