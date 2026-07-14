/**
 * HSE Operations - Frontend Application
 * Modular single-page application for HSE operational modules
 */

const HSEApp = (() => {
    'use strict';

    let currentUser = null;
    let currentModule = 'dashboard';
    let currentView = 'dashboard';

    function isAuthenticated() {
        return !!localStorage.getItem('hse_access_token');
    }

    async function get(url) {
        return window.API.get(url);
    }

    async function post(url, data) {
        return window.API.post(url, data);
    }

    async function put(url, data) {
        return window.API.put(url, data);
    }

    async function del(url) {
        return window.API.delete(url);
    }

    async function fetchWithAuth(url, options = {}) {
        const token = localStorage.getItem('hse_access_token');
        const headers = {
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };
        const response = await fetch(url, { ...options, headers });
        return response;
    }

    function $(selector) { return document.querySelector(selector); }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = 'position:fixed;bottom:20px;right:20px;padding:12px 20px;border-radius:8px;color:#fff;font-weight:600;z-index:9999;animation:slideIn .3s;';
        if (type === 'success') toast.style.background = '#2e7d32';
        else if (type === 'error') toast.style.background = '#c62828';
        else toast.style.background = '#1976d2';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="loading-state">Loading...</div>';
        }
    }

    function formatDate(dateStr) {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleDateString('id-ID');
    }

    function formatDateTime(dateStr) {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleString('id-ID');
    }

    const modules = {};

    function registerModule(name, module) {
        modules[name] = module;
    }

    function getModule(name) {
        return modules[name];
    }

    function navigateTo(module, view = 'dashboard') {
        currentModule = module;
        currentView = view;
        document.querySelectorAll('.module-view').forEach(el => el.style.display = 'none');
        const viewEl = document.getElementById(`view-${module}-${view}`);
        if (viewEl) {
            viewEl.style.display = 'block';
        }
        const mod = getModule(module);
        if (mod && mod.init) {
            mod.init(view);
        }
        updateNavigation();
    }

    function updateNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            const module = link.dataset.module;
            if (module === currentModule) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    async function init() {
        if (!isAuthenticated()) {
            showLogin();
            return;
        }

        try {
            const userData = await get('/auth/me');
            if (userData) {
                currentUser = userData;
                updateUserUI();
                renderDynamicMenu();
            }
        } catch (e) {
            console.error('Failed to load user:', e);
        }

        Object.values(modules).forEach(mod => {
            if (mod.initStatic) mod.initStatic();
        });

        navigateTo('dashboard');
    }

    function showLogin() {
        const loginView = document.getElementById('login-view');
        const appView = document.getElementById('app-view');
        if (loginView) loginView.style.display = 'flex';
        if (appView) appView.style.display = 'none';
    }

    function updateUserUI() {
        if (currentUser) {
            const userEl = document.getElementById('current-user');
            if (userEl) {
                userEl.textContent = currentUser.user_email || currentUser.email || 'User';
            }
        }
    }

    async function renderDynamicMenu() {
        try {
            const menuData = await get('/auth/menu');
            if (menuData && menuData.menu) {
                const menuContainer = document.getElementById('dynamic-menu');
                if (menuContainer) {
                    menuContainer.innerHTML = renderMenu(menuData.menu);
                }
            }
        } catch (e) {
            console.error('Failed to load menu:', e);
        }
    }

    function renderMenu(items) {
        return items.map(item => {
            if (item.children && item.children.length > 0) {
                const childrenHtml = item.children.map(child =>
                    `<a href="#" class="nav-link" data-module="${child.id}" onclick="HSEApp.navigateTo('${child.id}')">${child.label}</a>`
                ).join('');
                return `
                    <div class="nav-item">
                        <a href="#" class="nav-link">${item.icon || ''} ${item.label}</a>
                        <div class="nav-children">${childrenHtml}</div>
                    </div>
                `;
            }
            return `<a href="#" class="nav-link" data-module="${item.id}" onclick="HSEApp.navigateTo('${item.id}')">${item.icon || ''} ${item.label}</a>`;
        }).join('');
    }

    return {
        init,
        login: () => Auth.login(),
        logout: () => Auth.logout(),
        isAuthenticated,
        navigateTo,
        getModule,
        registerModule,
        $,
        showToast,
        formatDate,
        formatDateTime,
        get, post, put, del,
        fetchWithAuth
    };
})();

document.addEventListener('DOMContentLoaded', () => HSEApp.init());
