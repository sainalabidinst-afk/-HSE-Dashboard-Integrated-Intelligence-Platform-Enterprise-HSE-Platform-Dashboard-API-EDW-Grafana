/**
 * Near Miss Reports Module
 */

const NearMissModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('near-miss', {
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
        showLoading('near-miss-dashboard-content');
        try {
            const data = await HSEApp.get('/api/near-miss/dashboard');
            if (data) renderNearMissDashboard(data);
        } catch (error) {
            console.error('Failed to load near miss dashboard:', error);
            showToast('Failed to load near miss dashboard', 'error');
        }
    }

    function renderNearMissDashboard(data) {
        const container = document.getElementById('near-miss-dashboard-content');
        if (!container) return;

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi b"><div class="label">Total Reports</div><div class="val">${data.total_reports || 0}</div><div class="dot b"></div></div>
                <div class="card kpi a"><div class="label">Open</div><div class="val">${(data.by_status && data.by_status['Open']) || 0}</div><div class="dot a"></div></div>
                <div class="card kpi g"><div class="label">Closed</div><div class="val">${(data.by_status && data.by_status['Closed']) || 0}</div><div class="dot g"></div></div>
                <div class="card kpi r"><div class="label">Shared with Team</div><div class="val">${data.shared_with_team || 0}</div><div class="dot r"></div></div>
            </div>
            <div class="grid2">
                <div class="card"><div class="title">By Status</div><canvas id="near-miss-status-chart"></canvas></div>
                <div class="card"><div class="title">By Potential Severity</div><canvas id="near-miss-severity-chart"></canvas></div>
            </div>
        `;

        setTimeout(() => {
            initNearMissCharts(data);
        }, 100);
    }

    function initNearMissCharts(data) {
        const statusChart = document.getElementById('near-miss-status-chart');
        if (statusChart) {
            new Chart(statusChart, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data.by_status || {}),
                    datasets: [{
                        data: Object.values(data.by_status || {}),
                        backgroundColor: ['#fbc02d', '#2196f3', '#4caf50']
                    }]
                },
                options: { responsive: true }
            });
        }

        const severityChart = document.getElementById('near-miss-severity-chart');
        if (severityChart) {
            new Chart(severityChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.by_potential_severity || {}),
                    datasets: [{
                        label: 'Reports',
                        data: Object.values(data.by_potential_severity || {}),
                        backgroundColor: '#c62828'
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }

    async function loadList() {
        showLoading('near-miss-list-content');
        try {
            const data = await HSEApp.get(`/api/near-miss/list?page=${currentPage}&page_size=20`);
            if (data) renderNearMissList(data);
        } catch (error) {
            console.error('Failed to load near miss reports:', error);
            showToast('Failed to load near miss reports', 'error');
        }
    }

    function renderNearMissList(data) {
        const container = document.getElementById('near-miss-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.report_id}</td>
                <td>${HSEApp.formatDate(item.report_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.location || '-'}</td>
                <td>${item.category || '-'}</td>
                <td><span class="pill ${item.status === 'Closed' ? 'g' : item.status === 'Open' ? 'a' : 'gray'}">${item.status}</span></td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="alert('Near Miss form coming soon')">+ New Near Miss</button>
                <button class="btn btn-secondary" onclick="NearMissModule.refreshList()">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr><th>Report ID</th><th>Date</th><th>Site</th><th>Location</th><th>Category</th><th>Status</th></tr>
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
