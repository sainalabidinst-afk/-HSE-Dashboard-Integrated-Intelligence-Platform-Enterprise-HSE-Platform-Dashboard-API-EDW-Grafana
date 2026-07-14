# HSE Dashboard — API Migration Guide
## From CSV to API-Driven Architecture

This guide explains how the dashboard was migrated from CSV-based data loading to API-driven architecture.

---

## Architecture Overview

### Before (CSV-based)
```
Dashboard (index.html)
    │
    ├── Papa.parse("dummy_data/dim_site.csv")
    ├── Papa.parse("dummy_data/fact_hse_sample.csv")
    └── Papa.parse("dummy_data/...")
    │
    └── In-memory data processing
```

### After (API-driven)
```
Dashboard (index.html)
    │
    ├── js/api.js (API Client)
    ├── js/auth.js (Authentication)
    ├── js/store.js (State Management)
    └── js/app.js (Application Controller)
    │
    ▼
FastAPI Backend (localhost:8000)
    │
    ├── /api/auth/login
    ├── /api/dashboard/summary
    ├── /api/dashboard/incidents
    ├── /api/dashboard/ptw
    ├── /api/dashboard/training
    ├── /api/dashboard/environmental
    ├── /api/dashboard/equipment
    ├── /api/dashboard/contractor
    └── /api/dashboard/alerts
    │
    ▼
PostgreSQL EDW (hse_edw)
```

---

## File Structure

```
dashboard/
├── index.html              ← Main HTML (updated)
├── sites.geojson           ← Site location data
└── js/
    ├── api.js              ← Centralized API client
    ├── auth.js             ← Authentication module
    ├── store.js            ← State management
    └── app.js              ← Main application controller
```

---

## Key Changes

### 1. API Client (`js/api.js`)

**Before:**
```javascript
async function loadCSV(filename) {
  return new Promise((resolve, reject) => {
    Papa.parse(`dummy_data/${filename}`, {
      header: true,
      dynamicTyping: true,
      complete: (results) => resolve(results.data),
    });
  });
}
```

**After:**
```javascript
async function apiGet(endpoint, params = {}) {
  const queryString = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryString.append(key, value);
    }
  });
  const url = queryString.toString() ? `${endpoint}?${queryString.toString()}` : endpoint;
  return apiRequest(url, { method: 'GET' });
}
```

### 2. State Management (`js/store.js`)

**Before:**
```javascript
const DATA = {
  site: [], dept: [], employee: [], equipment: [], incident: [],
  contractor: [], ptw: [], environmental: [], training: [], fact_hse: [],
  ref_env_threshold: []
};
```

**After:**
```javascript
const DashboardStore = {
  state: {
    summary: null,
    incidents: null,
    ptw: null,
    training: null,
    environmental: null,
    equipment: null,
    contractor: null,
    alerts: [],
    loading: { summary: false, incidents: false, ... },
    error: { summary: null, incidents: null, ... },
    lastUpdated: {},
    filters: { site: 'all', period: 30 },
  },
  // ...
};
```

### 3. Data Loading (`js/app.js`)

**Before:**
```javascript
async function loadAllData() {
  const [site, dept, employee, ...] = await Promise.all([
    loadCSV('dim_site.csv'),
    loadCSV('dim_department.csv'),
    // ...
  ]);
  DATA.site = site; DATA.dept = dept; // ...
  populateFilters();
  initDashboard();
}
```

**After:**
```javascript
async init() {
  if (!API.isAuthenticated()) {
    this.showLogin();
    return;
  }
  this.setupEventListeners();
  this.setupFilters();
  await this.refreshAll();
  this.startAutoRefresh();
}
```

### 4. Rendering (`js/app.js`)

**Before:**
```javascript
function createKpiCard(containerId, label, value, unit, status, subtext) {
  const container = document.getElementById(containerId);
  const card = document.createElement('div');
  card.className = `kpi-card ${status}`;
  card.innerHTML = `...`;
  container.appendChild(card);
}
```

**After:**
```javascript
renderSummary() {
  const summary = DashboardStore.state.summary;
  if (loading) { /* show loading */ return; }
  if (error) { /* show error */ return; }
  if (!summary) { /* show empty */ return; }
  
  container.innerHTML = '';
  summary.kpis.forEach(kpi => {
    const card = document.createElement('div');
    card.className = `kpi ${status}`;
    card.innerHTML = `...`;
    container.appendChild(card);
  });
}
```

---

## Migration Steps

### Step 1: Backend API Ready

Ensure FastAPI backend is running:

```bash
cd backend
uvicorn app.main:app --reload
# Verify: http://localhost:8000/api/docs
```

### Step 2: Update Dashboard HTML

The `index.html` has been updated to:
- Remove PapaParse dependency
- Add new JS modules: `api.js`, `auth.js`, `store.js`, `app.js`
- Add login/logout UI
- Add loading/error states

### Step 3: Configure API Base URL

Set the API base URL in `js/api.js`:

```javascript
const API_BASE_URL = localStorage.getItem('API_BASE_URL') || 'http://localhost:8000';
```

Or set it dynamically from backend:

```html
<script>
  window.API_BASE_URL = 'http://localhost:8000';
</script>
```

### Step 4: Test Authentication

1. Open dashboard: `http://localhost:8080`
2. You should see login screen
3. Enter credentials: `admin@hse.local` / `password`
4. Dashboard loads with data from API

### Step 5: Verify Data Flow

Open browser DevTools → Network tab:

```
✓ GET http://localhost:8000/api/dashboard/summary?site_id=all&period_days=30
✓ GET http://localhost:8000/api/dashboard/incidents
✓ GET http://localhost:8000/api/dashboard/ptw
✓ GET http://localhost:8000/api/dashboard/training
✓ GET http://localhost:8000/api/dashboard/environmental
✓ GET http://localhost:8000/api/dashboard/equipment
✓ GET http://localhost:8000/api/dashboard/contractor
✓ GET http://localhost:8000/api/dashboard/alerts
```

---

## Auto-Refresh Configuration

The dashboard auto-refreshes at different intervals:

| Data Type | Interval | API Endpoint |
|-----------|----------|--------------|
| Alerts | 15 seconds | `/api/dashboard/alerts` |
| PTW | 30 seconds | `/api/dashboard/ptw` |
| Executive Summary | 60 seconds | `/api/dashboard/summary` |
| Environmental | 60 seconds | `/api/dashboard/environmental` |
| Incidents | 5 minutes | `/api/dashboard/incidents` |
| Training | 5 minutes | `/api/dashboard/training` |
| Equipment | 10 minutes | `/api/dashboard/equipment` |
| Contractor | 10 minutes | `/api/dashboard/contractor` |

Configure intervals in `js/app.js`:

```javascript
refreshIntervals: {
  alerts: 15000,
  ptw: 30000,
  summary: 60000,
  environmental: 60000,
  incidents: 300000,
  training: 300000,
  equipment: 600000,
  contractor: 600000,
},
```

---

## Error Handling

### Loading States
Each section shows loading spinner while fetching data:

```javascript
if (loading) {
  container.innerHTML = '<div class="loading-state">⏳ Loading...</div>';
  return;
}
```

### Error States
If API fails, show error with retry button:

```javascript
if (error) {
  container.innerHTML = `
    <div class="error-state">
      ⚠️ Failed to load data
      <button onclick="DashboardApp.refreshAll()">Retry</button>
    </div>
  `;
  return;
}
```

### Empty States
If API returns empty data:

```javascript
if (!data || data.length === 0) {
  container.innerHTML = '<div class="empty-state">No data available</div>';
  return;
}
```

---

## Authentication Flow

### Login Process

1. User enters credentials in login form
2. `Auth.login()` calls `POST /api/auth/login`
3. Backend returns JWT tokens
4. Tokens stored in `localStorage`
5. Dashboard reloads with authenticated state

### Token Refresh

1. API request returns 401
2. `apiRequest()` calls `refreshAccessToken()`
3. Uses refresh token to get new access token
4. Retries original request with new token
5. If refresh fails, user is logged out

### Logout

1. User clicks logout button
2. `Auth.logout()` clears tokens from `localStorage`
3. Dispatches `auth:logout` event
4. Dashboard shows login screen

---

## State Management

### Store Structure

```javascript
DashboardStore.state = {
  // Data
  summary: null,           // Executive summary KPIs
  incidents: null,         // Incident analysis
  ptw: null,               // PTW summary
  training: null,          // Training compliance
  environmental: null,     // Environmental data
  equipment: null,         // Equipment status
  contractor: null,        // Contractor performance
  alerts: [],              // Active alerts
  
  // UI State
  loading: { ... },        // Loading states per section
  error: { ... },          // Error messages per section
  lastUpdated: {},         // Timestamps
  
  // Filters
  filters: {
    site: 'all',
    period: 30,
  },
};
```

### Subscribing to Changes

Components can subscribe to state changes:

```javascript
DashboardStore.subscribe('summary', (newSummary) => {
  console.log('Summary updated:', newSummary);
  renderSummary(newSummary);
});
```

---

## Testing

### Manual Testing

1. **Start backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start dashboard:**
   ```bash
   cd dashboard
   python -m http.server 8080
   ```

3. **Open browser:** `http://localhost:8080`

4. **Login:** Use credentials from `security_user_role` table

5. **Verify:**
   - Dashboard loads without CSV errors
   - All charts render with API data
   - Filters work (site, period)
   - Auto-refresh works (wait 1 minute)
   - Logout works

### API Testing with curl

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@hse.local&password=password"

# Get summary (replace TOKEN with actual token)
curl "http://localhost:8000/api/dashboard/summary?site_id=all&period_days=30" \
  -H "Authorization: Bearer TOKEN"

# Get incidents
curl "http://localhost:8000/api/dashboard/incidents?site_id=all&period_days=30" \
  -H "Authorization: Bearer TOKEN"
```

### Automated Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app
```

---

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:

1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure dashboard origin is in the list
3. Restart backend after changing config

### 401 Unauthorized

If all requests return 401:

1. Check if tokens exist in `localStorage`
2. Try logging out and logging in again
3. Verify backend `/api/auth/login` works

### No Data Showing

If dashboard shows "No data available":

1. Check browser Network tab for failed requests
2. Verify backend is running: `http://localhost:8000/health`
3. Check database has data: `SELECT COUNT(*) FROM hse.fact_hse;`
4. Run ETL: `python scripts/etl_pipeline.py`

### Charts Not Rendering

If charts show "Loading..." forever:

1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify Chart.js is loaded
4. Check API response format matches expected schema

---

## Next Steps

After successful migration:

1. ✅ Dashboard uses API exclusively
2. 🔄 Remove PapaParse from HTML
3. 🔄 Remove `dummy_data/` loading code
4. 🔄 Add more detailed error messages
5. 🔄 Add request retry logic
6. 🔄 Implement offline mode (service worker)
7. 🔄 Add progressive web app (PWA) support

---

## Rollback Plan

If issues arise, you can rollback to CSV mode:

1. Keep original `index.html` as backup
2. Revert to CSV loading functions
3. Remove JS module dependencies
4. Restore PapaParse CDN link

The CSV files remain in `dummy_data/` as fallback.
