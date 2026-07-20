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
