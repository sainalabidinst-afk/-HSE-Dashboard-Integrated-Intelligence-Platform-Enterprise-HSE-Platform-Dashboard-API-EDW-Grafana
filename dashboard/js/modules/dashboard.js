/**
 * HSE Dashboard Module
 * Executive dashboard with KPI cards and charts
 */

const DashboardModule = (() => {
    let charts = {};

    function initStatic() {
        // Register module
        HSEApp.registerModule('dashboard', {
            init: initView
        });
    }

    async function initView(view) {
        if (view === 'dashboard') {
            await loadDashboardData();
        }
    }

    async function loadDashboardData() {
        showLoading('dashboard-content');

        try {
            const [summary, alerts] = await Promise.all([
                HSEApp.get('/dashboard/summary'),
                HSEApp.get('/dashboard/alerts')
            ]);

            renderKPICards(summary);
            renderAlerts(alerts);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            showToast('Failed to load dashboard data', 'error');
        }
    }

    function renderKPICards(summary) {
        const container = document.getElementById('kpi-cards');
        if (!container || !summary || !summary.kpis) return;

        container.innerHTML = summary.kpis.map(kpi => {
            const statusClass = kpi.status || 'gray';
            return `
                <div class="card kpi ${statusClass}">
                    <div class="label">${kpi.label}</div>
                    <div class="val">${kpi.value}${kpi.unit ? ' ' + kpi.unit : ''}</div>
                    <div class="sub">${kpi.subtext || ''}</div>
                    <div class="dot ${statusClass}"></div>
                </div>
            `;
        }).join('');
    }

    function renderAlerts(alerts) {
        const container = document.getElementById('active-alerts');
        if (!container) return;

        if (!alerts || alerts.length === 0) {
            container.innerHTML = '<div class="empty-state">No active alerts</div>';
            return;
        }

        container.innerHTML = alerts.slice(0, 5).map(alert => `
            <div class="alert ${alert.severity === 'critical' ? '' : 'warn'}">
                <div class="head">${alert.site_name || 'System'}: ${alert.message}</div>
                <div class="body">${alert.alert_type} - ${formatDateTime(alert.triggered_at)}</div>
            </div>
        `).join('');
    }

    return { initStatic, init: initView };
})();
