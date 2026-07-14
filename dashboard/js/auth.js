/**
 * HSE Dashboard — Authentication Module
 * 
 * Handles:
 * - Login/logout
 * - Token management
 * - Session state
 * - Role-based UI updates
 * - Dynamic menu
 */

const Auth = {
  /**
   * Login user
   * @param {string} username - Email or username
   * @param {string} password - Password
   * @returns {Promise<Object>} User data with tokens
   */
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store tokens and user info
    setTokens(data.access_token, data.refresh_token);
    setCurrentUser({
      email: username,
      role: data.user_role,
      site_access: data.site_access,
      can_export: data.can_export,
      can_edit: data.can_edit,
    });

    // Dispatch login event
    window.dispatchEvent(new Event('auth:login'));

    return data;
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await API.post('/api/auth/logout', {});
    } catch (e) {
      console.warn('Logout API failed:', e);
    }
    clearTokens();
    window.dispatchEvent(new Event('auth:logout'));
  },

  /**
   * Logout all sessions
   */
  async logoutAll() {
    try {
      await API.post('/api/auth/logout-all', {});
    } catch (e) {
      console.warn('Logout all failed:', e);
    }
    clearTokens();
    window.dispatchEvent(new Event('auth:logout'));
  },

  /**
   * Check if user is logged in
   */
  isLoggedIn() {
    return !!getAccessToken();
  },

  /**
   * Get current user
   */
  getCurrentUser() {
    return getCurrentUser();
  },

  /**
   * Refresh token
   */
  async refreshToken() {
    return await refreshAccessToken();
  },

  /**
   * Fetch dynamic menu from API
   */
  async fetchMenu() {
    try {
      const response = await API.get('/api/auth/menu');
      return response;
    } catch (error) {
      console.error('Failed to fetch menu:', error);
      return null;
    }
  },

  /**
   * Update UI based on user role
   */
  updateUIForRole() {
    const user = getCurrentUser();
    if (!user) return;

    // Show/hide elements based on role
    document.body.classList.remove('role-admin', 'role-manager', 'role-hse', 'role-supervisor', 'role-auditor', 'role-guest');

    const roleClass = `role-${user.role.toLowerCase()}`;
    document.body.classList.add(roleClass);

    // Update user info in UI
    const userInfoEl = document.getElementById('userInfo');
    if (userInfoEl) {
      userInfoEl.textContent = `${user.name} (${user.role})`;
    }

    // Show/hide menu items based on permissions
    this.updateMenuVisibility(user);
  },

  /**
   * Update menu visibility based on user permissions
   */
  updateMenuVisibility(user) {
    // This can be extended based on your menu structure
    const menuItems = document.querySelectorAll('[data-required-role]');
    menuItems.forEach(item => {
      const requiredRoles = item.dataset.requiredRole.split(',');
      const hasAccess = requiredRoles.includes(user.role) || requiredRoles.includes('ALL');
      item.style.display = hasAccess ? '' : 'none';
    });
  },

  /**
   * Render dynamic menu from API
   */
  renderMenu(menuData) {
    const menuContainer = document.getElementById('dynamicMenu');
    if (!menuContainer || !menuData) return;

    const menu = menuData.menu || [];
    let html = '<nav class="nav-menu">';

    menu.forEach(item => {
      if (item.children && item.children.length > 0) {
        html += `
          <div class="nav-item has-children">
            <a href="#" class="nav-link">${item.icon || ''} ${item.label}</a>
            <div class="nav-children">
              ${item.children.map(child => `
                <a href="${child.id}.html" class="nav-link" data-permission="${child.permission || ''}">
                  ${child.label}
                </a>
              `).join('')}
            </div>
          </div>
        `;
      } else {
        html += `
          <div class="nav-item">
            <a href="${item.id}.html" class="nav-link" data-permission="${item.permission || ''}">
              ${item.icon || ''} ${item.label}
            </a>
          </div>
        `;
      }
    });

    html += '</nav>';
    menuContainer.innerHTML = html;
  },

  /**
   * Initialize auth module
   */
  init() {
    // Listen for auth events
    window.addEventListener('auth:login', async () => {
      this.updateUIForRole();
      // Fetch and render dynamic menu
      const menuData = await this.fetchMenu();
      if (menuData) {
        this.renderMenu(menuData);
      }
    });

    window.addEventListener('auth:logout', () => {
      // Redirect to login page or show login modal
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    });

    // Check if user is already logged in
    if (this.isLoggedIn()) {
      this.updateUIForRole();
    }
  },
};

// Export for use in other modules
window.Auth = Auth;
