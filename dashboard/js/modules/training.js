/**
 * Training Management Module
 */

const TrainingModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('training', {
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
        showLoading('training-dashboard-content');

        try {
            const data = await HSEApp.get('/api/training/dashboard');
            if (data) {
                renderTrainingDashboard(data);
            }
        } catch (error) {
            console.error('Failed to load training dashboard:', error);
            showToast('Failed to load training dashboard', 'error');
        }
    }

    function renderTrainingDashboard(data) {
        const container = document.getElementById('training-dashboard-content');
        if (!container) return;

        const complianceRate = data.total_records > 0
            ? Math.round((data.completed || 0) / data.total_records * 100)
            : 0;

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi b">
                    <div class="label">Total Records</div>
                    <div class="val">${data.total_records || 0}</div>
                    <div class="sub">Training records</div>
                    <div class="dot b"></div>
                </div>
                <div class="card kpi g">
                    <div class="label">Completed</div>
                    <div class="val">${data.completed || 0}</div>
                    <div class="sub">Passed</div>
                    <div class="dot g"></div>
                </div>
                <div class="card kpi a">
                    <div class="label">Pending</div>
                    <div class="val">${data.pending || 0}</div>
                    <div class="sub">In progress</div>
                    <div class="dot a"></div>
                </div>
                <div class="card kpi ${complianceRate < 80 ? 'r' : 'g'}">
                    <div class="label">Compliance</div>
                    <div class="val">${complianceRate}%</div>
                    <div class="dot ${complianceRate < 80 ? 'r' : 'g'}"></div>
                </div>
            </div>

            <div class="grid2">
                <div class="card">
                    <div class="title">By Result</div>
                    <canvas id="training-result-chart"></canvas>
                </div>
                <div class="card">
                    <div class="title">By Type</div>
                    <canvas id="training-type-chart"></canvas>
                </div>
            </div>
        `;

        setTimeout(() => {
            initTrainingCharts(data);
        }, 100);
    }

    function initTrainingCharts(data) {
        const resultChart = document.getElementById('training-result-chart');
        if (resultChart) {
            new Chart(resultChart, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.by_result || {}),
                    datasets: [{
                        data: Object.values(data.by_result || {}),
                        backgroundColor: ['#4caf50', '#f44336', '#fbc02d', '#2196f3']
                    }]
                },
                options: { responsive: true }
            });
        }

        const typeChart = document.getElementById('training-type-chart');
        if (typeChart) {
            new Chart(typeChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.by_type || {}),
                    datasets: [{
                        label: 'Records',
                        data: Object.values(data.by_type || {}),
                        backgroundColor: '#2196f3'
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }

    async function loadList() {
        showLoading('training-list-content');

        try {
            const data = await HSEApp.get(`/api/training/list?page=${currentPage}&page_size=20`);
            if (data) {
                renderTrainingList(data);
            }
        } catch (error) {
            console.error('Failed to load training records:', error);
            showToast('Failed to load training records', 'error');
        }
    }

    function renderTrainingList(data) {
        const container = document.getElementById('training-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.record_id}</td>
                <td>${formatDate(item.training_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.training_name || '-'}</td>
                <td>${item.training_type || '-'}</td>
                <td><span class="pill ${item.result === 'Pass' ? 'g' : item.result === 'Fail' ? 'r' : 'a'}">${item.result}</span></td>
                <td>${item.trainer || '-'}</td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('training', 'add')">+ New Training</button>
                <button class="btn btn-secondary" onclick="TrainingModule.refreshList()">Refresh</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Record ID</th>
                        <th>Date</th>
                        <th>Site</th>
                        <th>Training Name</th>
                        <th>Type</th>
                        <th>Result</th>
                        <th>Trainer</th>
                    </tr>
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
