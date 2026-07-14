/**
 * Contractor Management Module
 */

const ContractorModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('contractors', {
            init: initView
        });
    }

    async function initView(view) {
        currentPage = 1;
        if (view === 'list') {
            await loadList();
        }
    }

    async function loadList() {
        showLoading('contractor-list-content');
        try {
            const data = await HSEApp.get(`/api/contractors/records?page=${currentPage}&page_size=20`);
            if (data) renderContractorList(data);
        } catch (error) {
            console.error('Failed to load contractor records:', error);
            showToast('Failed to load contractor records', 'error');
        }
    }

    function renderContractorList(data) {
        const container = document.getElementById('contractor-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.record_id}</td>
                <td>${item.contractor_id || '-'}</td>
                <td>${HSEApp.formatDate(item.record_date)}</td>
                <td>${item.record_type || '-'}</td>
                <td>${item.site_id || '-'}</td>
                <td><span class="pill ${item.result === 'Pass' ? 'g' : item.result === 'Fail' ? 'r' : 'a'}">${item.result || '-'}</span></td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="alert('Contractor record form coming soon')">+ New Record</button>
                <button class="btn btn-secondary" onclick="ContractorModule.refreshList()">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr><th>Record ID</th><th>Contractor ID</th><th>Date</th><th>Type</th><th>Site</th><th>Result</th></tr>
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
