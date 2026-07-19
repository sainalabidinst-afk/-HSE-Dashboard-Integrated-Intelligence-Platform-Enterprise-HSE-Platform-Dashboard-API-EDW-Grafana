/**
 * HIRA / JSA Assessments Module
 */

const HIRAModule = (() => {
    let currentPage = 1;

    function initStatic() {
        HSEApp.registerModule('hira', {
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
        showLoading('hira-list-content');
        try {
            const data = await HSEApp.get(`/api/hira/list?page=${currentPage}&page_size=20`);
            if (data) renderHIRAList(data);
        } catch (error) {
            console.error('Failed to load HIRA assessments:', error);
            showToast('Failed to load HIRA assessments', 'error');
        }
    }

    function renderHIRAList(data) {
        const container = document.getElementById('hira-list-content');
        if (!container) return;

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.assessment_id}</td>
                <td>${HSEApp.formatDate(item.assessment_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.activity || '-'}</td>
                <td><span class="pill ${item.risk_rating === 'Extreme' || item.risk_rating === 'High' ? 'r' : item.risk_rating === 'Medium' ? 'a' : 'g'}">${item.risk_rating}</span></td>
                <td>${item.risk_score || '-'}</td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('hira', 'add')">+ New HIRA</button>
                <button class="btn btn-secondary" onclick="HIRAModule.refreshList()">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr><th>Assessment ID</th><th>Date</th><th>Site</th><th>Activity</th><th>Risk Rating</th><th>Risk Score</th></tr>
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
