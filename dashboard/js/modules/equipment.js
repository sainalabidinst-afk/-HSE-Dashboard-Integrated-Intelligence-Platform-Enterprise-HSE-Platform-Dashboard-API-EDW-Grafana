/**
 * Equipment Inspections Module
 */

const EquipmentModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('equipment', {
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
        showLoading('equipment-dashboard-content');
        try {
            const data = await HSEApp.get('/api/dashboard/equipment');
            if (data) renderEquipmentDashboard(data);
        } catch (error) {
            console.error('Failed to load equipment dashboard:', error);
            showToast('Failed to load equipment dashboard', 'error');
        }
    }

    function renderEquipmentDashboard(data) {
        const container = document.getElementById('equipment-dashboard-content');
        if (!container) return;

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi b"><div class="label">Total Equipment</div><div class="val">${data.total_equipment || 0}</div><div class="dot b"></div></div>
                <div class="card kpi g"><div class="label">Valid Cert</div><div class="val">${data.valid_cert || 0}</div><div class="dot g"></div></div>
                <div class="card kpi r"><div class="label">Expired Cert</div><div class="val">${data.expired_cert || 0}</div><div class="dot r"></div></div>
                <div class="card kpi a"><div class="label">Overdue Inspection</div><div class="val">${data.overdue_inspection || 0}</div><div class="dot a"></div></div>
            </div>
        `;
    }

    async function loadList() {
        showLoading('equipment-list-content');
        try {
            const data = await HSEApp.get(`/api/equipment/inspections?page=${currentPage}&page_size=20`);
            if (data) renderEquipmentList(data);
        } catch (error) {
            console.error('Failed to load equipment inspections:', error);
            showToast('Failed to load equipment inspections', 'error');
        }
    }

    function renderEquipmentList(data) {
        const container = document.getElementById('equipment-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.inspection_id}</td>
                <td>${item.equipment_id || '-'}</td>
                <td>${HSEApp.formatDate(item.inspection_date)}</td>
                <td>${item.inspector || '-'}</td>
                <td><span class="pill ${item.result === 'Pass' ? 'g' : item.result === 'Fail' ? 'r' : 'a'}">${item.result}</span></td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('equipment', 'add')">+ New Inspection</button>
                <button class="btn btn-secondary" onclick="EquipmentModule.refreshList()">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr><th>Inspection ID</th><th>Equipment ID</th><th>Date</th><th>Inspector</th><th>Result</th></tr>
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
