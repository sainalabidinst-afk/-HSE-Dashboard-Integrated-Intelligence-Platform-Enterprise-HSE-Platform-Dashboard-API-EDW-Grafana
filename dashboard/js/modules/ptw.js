/**
 * PTW (Permit to Work) Module
 */

const PTWModule = (() => {
    let currentPage = 1;
    let currentFilters = {};

    function initStatic() {
        HSEApp.registerModule('ptw', {
            init: initView
        });
    }

    async function initView(view) {
        currentPage = 1;
        currentFilters = {};

        if (view === 'dashboard') {
            await loadDashboard();
        } else if (view === 'list') {
            await loadList();
        }
    }

    async function loadDashboard() {
        showLoading('ptw-dashboard-content');

        try {
            const data = await HSEApp.get('/api/ptw/dashboard');
            if (data) {
                renderPTWDashboard(data);
            }
        } catch (error) {
            console.error('Failed to load PTW dashboard:', error);
            showToast('Failed to load PTW dashboard', 'error');
        }
    }

    function renderPTWDashboard(data) {
        const container = document.getElementById('ptw-dashboard-content');
        if (!container) return;

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi b">
                    <div class="label">Total Requests</div>
                    <div class="val">${data.total_requests || 0}</div>
                    <div class="sub">This period</div>
                    <div class="dot b"></div>
                </div>
                <div class="card kpi g">
                    <div class="label">Active Permits</div>
                    <div class="val">${data.active_permits || 0}</div>
                    <div class="sub">Currently active</div>
                    <div class="dot g"></div>
                </div>
                <div class="card kpi r">
                    <div class="label">Expired</div>
                    <div class="val">${data.expired_permits || 0}</div>
                    <div class="sub">Need renewal</div>
                    <div class="dot r"></div>
                </div>
                <div class="card kpi a">
                    <div class="label">Violations</div>
                    <div class="val">${data.total_violations || 0}</div>
                    <div class="sub">Total violations</div>
                    <div class="dot a"></div>
                </div>
            </div>

            <div class="grid2">
                <div class="card">
                    <div class="title">By Status</div>
                    <canvas id="ptw-status-chart"></canvas>
                </div>
                <div class="card">
                    <div class="title">By Type</div>
                    <canvas id="ptw-type-chart"></canvas>
                </div>
            </div>
        `;

        setTimeout(() => {
            initPTWCharts(data);
        }, 100);
    }

    function initPTWCharts(data) {
        const statusChart = document.getElementById('ptw-status-chart');
        if (statusChart) {
            new Chart(statusChart, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data.by_status || {}),
                    datasets: [{
                        data: Object.values(data.by_status || {}),
                        backgroundColor: ['#9e9e9e', '#fbc02d', '#4caf50', '#f44336', '#2196f3', '#2e7d32', '#c62828']
                    }]
                },
                options: { responsive: true }
            });
        }

        const typeChart = document.getElementById('ptw-type-chart');
        if (typeChart) {
            new Chart(typeChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.by_type || {}),
                    datasets: [{
                        label: 'PTWs',
                        data: Object.values(data.by_type || {}),
                        backgroundColor: '#2196f3'
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }
    }

    async function loadList() {
        showLoading('ptw-list-content');

        try {
            const data = await HSEApp.get(`/api/ptw/list?page=${currentPage}&page_size=20`);
            if (data) {
                renderPTWList(data);
            }
        } catch (error) {
            console.error('Failed to load PTWs:', error);
            showToast('Failed to load PTWs', 'error');
        }
    }

    function renderPTWList(data) {
        const container = document.getElementById('ptw-list-content');
        if (!container) return;

        const statusColors = {
            'Draft': 'gray', 'Pending Approval': 'yellow', 'Approved': 'blue',
            'Active': 'green', 'Expired': 'red', 'Closed': 'green', 'Cancelled': 'red'
        };

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.request_id}</td>
                <td>${window.formatDate(item.request_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.workstation || '-'}</td>
                <td>${item.ptw_type || '-'}</td>
                <td>${window.formatDateTime(item.start_at)}</td>
                <td><span class="pill ${statusColors[item.ptw_status] || 'gray'}">${item.ptw_status}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="PTWModule.viewDetail('${item.request_id}')">View</button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('ptw', 'add')">+ New PTW</button>
                <button class="btn btn-secondary" onclick="PTWModule.refreshList()">Refresh</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Date</th>
                        <th>Site</th>
                        <th>Workstation</th>
                        <th>Type</th>
                        <th>Start At</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>

            <div class="pagination">
                <button class="btn btn-sm" ${currentPage <= 1 ? 'disabled' : ''} onclick="PTWModule.goToPage(${currentPage - 1})">Previous</button>
                <span>Page ${data.page} of ${data.total_pages}</span>
                <button class="btn btn-sm" ${currentPage >= data.total_pages ? 'disabled' : ''} onclick="PTWModule.goToPage(${currentPage + 1})">Next</button>
            </div>
        `;
    }

    function goToPage(page) {
        currentPage = page;
        loadList();
    }

    function refreshList() {
        loadList();
    }

    async function viewDetail(requestId) {
        const container = document.getElementById('ptw-detail-container');
        if (!container) return;

        showLoading('ptw-detail-container');

        try {
            const data = await HSEApp.get(`/api/ptw/${requestId}`);
            if (!data) {
                showToast('PTW not found', 'error');
                return;
            }

            container.innerHTML = `
                <div class="page-header">
                    <h2>PTW Detail - ${data.request_id}</h2>
                    <div class="page-actions">
                        <button class="btn btn-secondary" onclick="HSEApp.navigateTo('ptw', 'list')">Back</button>
                    </div>
                </div>
                <div class="detail-grid">
                    <div class="card">
                        <h3>PTW Information</h3>
                        <div class="detail-row"><span class="detail-label">Request ID:</span><span class="detail-value">${data.request_id}</span></div>
                        <div class="detail-row"><span class="detail-label">Site:</span><span class="detail-value">${data.site_id || '-'}</span></div>
                        <div class="detail-row"><span class="detail-label">Workstation:</span><span class="detail-value">${data.workstation || '-'}</span></div>
                        <div class="detail-row"><span class="detail-label">Type:</span><span class="detail-value">${data.ptw_type || '-'}</span></div>
                        <div class="detail-row"><span class="detail-label">Status:</span><span class="detail-value">${data.ptw_status}</span></div>
                        <div class="detail-row"><span class="detail-label">PIC:</span><span class="detail-value">${data.pic || '-'}</span></div>
                    </div>
                    <div class="card">
                        <h3>Hazards & Controls</h3>
                        <p><strong>Hazards:</strong> ${data.hazard_identified || 'None'}</p>
                        <p><strong>Mitigation:</strong> ${data.mitigation_list || 'None'}</p>
                        <p><strong>Isolation:</strong> ${data.isolation_list || 'None'}</p>
                    </div>
                </div>
            `;

            HSEApp.navigateTo('ptw', 'detail');
        } catch (error) {
            console.error('Failed to load PTW detail:', error);
            showToast('Failed to load PTW detail', 'error');
        }
    }

    return { initStatic, init: initView };
})();
