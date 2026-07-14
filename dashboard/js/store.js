/**
 * HSE Dashboard — State Management Store
 * 
 * Centralized state for dashboard data.
 * Components subscribe to store updates.
 * 
 * Architecture:
 * DashboardStore holds all data
 * Components call: DashboardStore.getSummary(), etc.
 * Store fetches from API and caches
 */

const DashboardStore = {
  // State
  state: {
    summary: null,
    incidents: null,
    ptw: null,
    training: null,
    environmental: null,
    equipment: null,
    contractor: null,
    alerts: [],
    loading: {
      summary: false,
      incidents: false,
      ptw: false,
      training: false,
      environmental: false,
      equipment: false,
      contractor: false,
      alerts: false,
    },
    error: {
      summary: null,
      incidents: null,
      ptw: null,
      training: null,
      environmental: null,
      equipment: null,
      contractor: null,
      alerts: null,
    },
    lastUpdated: {},
    filters: {
      site: 'all',
      period: 30,
    },
  },

  // Subscribers
  listeners: {},

  /**
   * Subscribe to state changes
   * @param {string} key - State key to subscribe to
   * @param {Function} callback - Function to call when state changes
   */
  subscribe(key, callback) {
    if (!this.listeners[key]) {
      this.listeners[key] = [];
    }
    this.listeners[key].push(callback);
  },

  /**
   * Notify subscribers of state change
   * @param {string} key - State key that changed
   * @param {*} value - New value
   */
  notify(key, value) {
    if (this.listeners[key]) {
      this.listeners[key].forEach(callback => callback(value));
    }
  },

  /**
   * Update state and notify subscribers
   * @param {string} key - State key to update
   * @param {*} value - New value
   */
  setState(key, value) {
    this.state[key] = value;
    this.notify(key, value);
  },

  /**
   * Set loading state
   * @param {string} key - State key
   * @param {boolean} isLoading - Loading state
   */
  setLoading(key, isLoading) {
    this.state.loading[key] = isLoading;
    this.notify(`loading.${key}`, isLoading);
  },

  /**
   * Set error state
   * @param {string} key - State key
   * @param {string|null} error - Error message or null
   */
  setError(key, error) {
    this.state.error[key] = error;
    this.notify(`error.${key}`, error);
  },

  /**
   * Fetch executive summary from API
   */
  async fetchSummary() {
    this.setLoading('summary', true);
    this.setError('summary', null);

    try {
      const params = {
        site_id: this.state.filters.site,
        period_days: this.state.filters.period,
      };

      const data = await API.get('/api/dashboard/summary', params);
      this.setState('summary', data);
      this.state.lastUpdated.summary = new Date().toISOString();
    } catch (error) {
      this.setError('summary', error.message);
      console.error('Failed to fetch summary:', error);
    } finally {
      this.setLoading('summary', false);
    }
  },

  /**
   * Fetch incidents from API
   */
  async fetchIncidents() {
    this.setLoading('incidents', false);
    this.setError('incidents', null);

    try {
      const params = {
        site_id: this.state.filters.site,
        period_days: this.state.filters.period,
      };

      const data = await API.get('/api/dashboard/incidents', params);
      this.setState('incidents', data);
      this.state.lastUpdated.incidents = new Date().toISOString();
    } catch (error) {
      this.setError('incidents', error.message);
      console.error('Failed to fetch incidents:', error);
    } finally {
      this.setLoading('incidents', false);
    }
  },

  /**
   * Fetch PTW from API
   */
  async fetchPTW() {
    this.setLoading('ptw', true);
    this.setError('ptw', null);

    try {
      const params = {
        site_id: this.state.filters.site,
        period_days: this.state.filters.period,
      };

      const data = await API.get('/api/dashboard/ptw', params);
      this.setState('ptw', data);
      this.state.lastUpdated.ptw = new Date().toISOString();
    } catch (error) {
      this.setError('ptw', error.message);
      console.error('Failed to fetch PTW:', error);
    } finally {
      this.setLoading('ptw', false);
    }
  },

  /**
   * Fetch training from API
   */
  async fetchTraining() {
    this.setLoading('training', true);
    this.setError('training', null);

    try {
      const params = {
        site_id: this.state.filters.site,
        period_days: this.state.filters.period,
      };

      const data = await API.get('/api/dashboard/training', params);
      this.setState('training', data);
      this.state.lastUpdated.training = new Date().toISOString();
    } catch (error) {
      this.setError('training', error.message);
      console.error('Failed to fetch training:', error);
    } finally {
      this.setLoading('training', false);
    }
  },

  /**
   * Fetch environmental from API
   */
  async fetchEnvironmental() {
    this.setLoading('environmental', true);
    this.setError('environmental', null);

    try {
      const params = {
        site_id: this.state.filters.site,
        period_days: this.state.filters.period,
      };

      const data = await API.get('/api/dashboard/environmental', params);
      this.setState('environmental', data);
      this.state.lastUpdated.environmental = new Date().toISOString();
    } catch (error) {
      this.setError('environmental', error.message);
      console.error('Failed to fetch environmental:', error);
    } finally {
      this.setLoading('environmental', false);
    }
  },

  /**
   * Fetch equipment from API
   */
  async fetchEquipment() {
    this.setLoading('equipment', true);
    this.setError('equipment', null);

    try {
      const params = {
        site_id: this.state.filters.site,
      };

      const data = await API.get('/api/dashboard/equipment', params);
      this.setState('equipment', data);
      this.state.lastUpdated.equipment = new Date().toISOString();
    } catch (error) {
      this.setError('equipment', error.message);
      console.error('Failed to fetch equipment:', error);
    } finally {
      this.setLoading('equipment', false);
    }
  },

  /**
   * Fetch contractor from API
   */
  async fetchContractor() {
    this.setLoading('contractor', true);
    this.setError('contractor', null);

    try {
      const data = await API.get('/api/dashboard/contractor');
      this.setState('contractor', data);
      this.state.lastUpdated.contractor = new Date().toISOString();
    } catch (error) {
      this.setError('contractor', error.message);
      console.error('Failed to fetch contractor:', error);
    } finally {
      this.setLoading('contractor', false);
    }
  },

  /**
   * Fetch alerts from API
   */
  async fetchAlerts() {
    this.setLoading('alerts', true);
    this.setError('alerts', null);

    try {
      const params = {
        site_id: this.state.filters.site,
      };

      const data = await API.get('/api/dashboard/alerts', params);
      this.setState('alerts', data);
      this.state.lastUpdated.alerts = new Date().toISOString();
    } catch (error) {
      this.setError('alerts', error.message);
      console.error('Failed to fetch alerts:', error);
    } finally {
      this.setLoading('alerts', false);
    }
  },

  /**
   * Fetch all dashboard data
   */
  async fetchAll() {
    const promises = [
      this.fetchSummary(),
      this.fetchIncidents(),
      this.fetchPTW(),
      this.fetchTraining(),
      this.fetchEnvironmental(),
      this.fetchEquipment(),
      this.fetchContractor(),
      this.fetchAlerts(),
    ];

    try {
      await Promise.all(promises);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  },

  /**
   * Update filters and refetch data
   * @param {Object} newFilters - New filter values
   */
  async updateFilters(newFilters) {
    this.state.filters = { ...this.state.filters, ...newFilters };
    await this.fetchAll();
  },

  /**
   * Clear all cached data
   */
  clearCache() {
    this.state.summary = null;
    this.state.incidents = null;
    this.state.ptw = null;
    this.state.training = null;
    this.state.environmental = null;
    this.state.equipment = null;
    this.state.contractor = null;
    this.state.alerts = [];
    this.state.lastUpdated = {};
  },
};

// Export for use in other modules
window.DashboardStore = DashboardStore;
