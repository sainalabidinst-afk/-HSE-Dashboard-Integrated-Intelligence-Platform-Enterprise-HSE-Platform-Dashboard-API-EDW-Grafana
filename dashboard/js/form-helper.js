/**
 * Form Helper - Generic form handler for all modules
 */
const FormHelper = {
    loadSites: async function() {
        if (window.cachedSites) return window.cachedSites;
        try {
            const sites = await HSEApp.get('/api/sites/');
            window.cachedSites = sites || [];
            return window.cachedSites;
        } catch {
            return [{site_id: 'SITE-A', site_name: 'Site Alpha Kutai'}, {site_id: 'SITE-B', site_name: 'Site Beta Balikpapan'}, {site_id: 'SITE-C', site_name: 'Site Gamma Samarinda'}];
        }
    },

    renderSiteOptions: function(sites) {
        return sites.map(s => '<option value="' + s.site_id + '">' + s.site_name + '</option>').join('');
    },

    bindSave: function(moduleName, endpoint, navigateBack) {
        return async function() {
            const form = document.getElementById(moduleName + '-form');
            const data = {};
            form.querySelectorAll('input, select, textarea').forEach(el => {
                if (el.id) data[el.id.replace(moduleName + '-', '')] = el.type === 'checkbox' ? el.checked : el.value;
            });
            try {
                await HSEApp.post('/api/' + endpoint + '/', data);
                showToast(moduleName + ' created', 'success');
                HSEApp.navigateTo(moduleName, navigateBack);
            } catch(e) {
                showToast('Failed: ' + e.message, 'error');
            }
        };
    }
};