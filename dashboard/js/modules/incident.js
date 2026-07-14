/**
 * Incident Management Module
 * Full CRUD operations for incident reports
 */

const IncidentModule = (() => {
    let currentPage = 1;
    let currentFilters = {};
    let editingId = null;

    function initStatic() {
        HSEApp.registerModule('incidents', {
            init: initView
        });
    }

    async function initView(view) {
        editingId = null;
        currentPage = 1;
        currentFilters = {};

        if (view === 'dashboard') {
            await loadDashboard();
        } else if (view === 'list') {
            await loadList();
        } else if (view === 'add' || view === 'edit') {
            showForm(view);
        } else if (view === 'detail') {
            // Handled by navigation
        }
    }

    // =============================================
    // DASHBOARD
    // =============================================

    async function loadDashboard() {
        showLoading('incident-dashboard-content');

        try {
            const data = await HSEApp.get('/api/incidents/dashboard');
            if (data) {
                renderIncidentDashboard(data);
            }
        } catch (error) {
            console.error('Failed to load incident dashboard:', error);
            showToast('Failed to load dashboard data', 'error');
        }
    }

    function renderIncidentDashboard(data) {
        const container = document.getElementById('incident-dashboard-content');
        if (!container) return;

        const severityColors = {
            'Fatality': 'red', 'LTI': 'red', 'MTI': 'orange',
            'First Aid': 'yellow', 'Near Miss': 'blue', 'Property Damage': 'gray'
        };

        container.innerHTML = `
            <div class="grid1">
                <div class="card kpi r">
                    <div class="label">Total Reports</div>
                    <div class="val">${data.total_reports || 0}</div>
                    <div class="sub">Period: ${formatDate(data.period_start)} - ${formatDate(data.period_end)}</div>
                    <div class="dot r"></div>
                </div>
                <div class="card kpi ${data.overdue_investigations > 0 ? 'r' : 'g'}">
                    <div class="label">Open Investigations</div>
                    <div class="val">${data.open_investigations || 0}</div>
                    <div class="sub">${data.overdue_investigations || 0} overdue</div>
                    <div class="dot ${data.overdue_investigations > 0 ? 'r' : 'g'}"></div>
                </div>
                <div class="card kpi r">
                    <div class="label">Lost Days</div>
                    <div class="val">${data.total_lost_days || 0}</div>
                    <div class="sub">Total lost work days</div>
                    <div class="dot r"></div>
                </div>
                <div class="card kpi a">
                    <div class="label">Restricted Days</div>
                    <div class="val">${data.total_restricted_days || 0}</div>
                    <div class="sub">Total restricted work days</div>
                    <div class="dot a"></div>
                </div>
            </div>

            <div class="grid2">
                <div class="card">
                    <div class="title">By Severity</div>
                    ${renderBarChart('incident-severity-chart', data.by_severity || {}, severityColors)}
                </div>
                <div class="card">
                    <div class="title">By Status</div>
                    ${renderBarChart('incident-status-chart', data.by_status || {}, {})}
                </div>
            </div>

            <div class="grid2">
                <div class="card">
                    <div class="title">By Category</div>
                    ${renderBarChart('incident-category-chart', data.by_category || {}, {})}
                </div>
                <div class="card">
                    <div class="title">By Site</div>
                    ${renderBarChart('incident-site-chart', data.by_site || {}, {})}
                </div>
            </div>

            <div class="card">
                <div class="title">Trend (Last ${data.period_start} to ${data.period_end})</div>
                ${renderTrendChart('incident-trend-chart', data.trend || [])}
            </div>
        `;

        // Initialize charts
        setTimeout(() => {
            initIncidentCharts(data);
        }, 100);
    }

    function initIncidentCharts(data) {
        const severityChart = document.getElementById('incident-severity-chart');
        if (severityChart) {
            new Chart(severityChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.by_severity || {}),
                    datasets: [{
                        label: 'Incidents',
                        data: Object.values(data.by_severity || {}),
                        backgroundColor: ['#c62828', '#d84315', '#f57c00', '#fbc02d', '#1976d2', '#757575']
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        const trendChart = document.getElementById('incident-trend-chart');
        if (trendChart && data.trend) {
            new Chart(trendChart, {
                type: 'line',
                data: {
                    labels: data.trend.map(t => t.date),
                    datasets: [{
                        label: 'Incidents',
                        data: data.trend.map(t => t.count),
                        borderColor: '#c62828',
                        tension: 0.3
                    }]
                },
                options: { responsive: true }
            });
        }
    }

    function renderBarChart(canvasId, data, colorMap) {
        const colors = {
            'Fatality': '#c62828', 'LTI': '#d84315', 'MTI': '#f57c00', 'First Aid': '#fbc02d',
            'Near Miss': '#1976d2', 'Property Damage': '#757575',
            'Draft': '#9e9e9e', 'Submitted': '#fbc02d', 'Under Review': '#2196f3',
            'Approved': '#4caf50', 'Closed': '#2e7d32', 'Injury': '#c62828',
            'Near Miss': '#1976d2', 'Property Damage': '#757575'
        };

        return `<canvas id="${canvasId}"></canvas>`;
    }

    function renderTrendChart(canvasId, data) {
        return `<canvas id="${canvasId}"></canvas>`;
    }

    // =============================================
    // LIST VIEW
    // =============================================

    async function loadList() {
        showLoading('incident-list-content');

        const queryParams = new URLSearchParams({
            page: currentPage,
            page_size: 20,
            ...currentFilters
        });

        try {
            const data = await HSEApp.get(`/api/incidents/list?${queryParams}`);
            if (data) {
                renderIncidentList(data);
            }
        } catch (error) {
            console.error('Failed to load incidents:', error);
            showToast('Failed to load incidents', 'error');
        }
    }

    function renderIncidentList(data) {
        const container = document.getElementById('incident-list-content');
        if (!container) return;

        const severityColors = {
            'Fatality': 'red', 'LTI': 'red', 'MTI': 'orange',
            'First Aid': 'yellow', 'Near Miss': 'blue', 'Property Damage': 'gray'
        };

        const rows = (data.items || []).map(item => `
            <tr>
                <td>${item.report_id}</td>
                <td>${formatDate(item.report_date)}</td>
                <td>${item.site_id || '-'}</td>
                <td>${item.location || '-'}</td>
                <td><span class="pill ${severityColors[item.severity] || 'gray'}">${item.severity}</span></td>
                <td>${item.incident_type || '-'}</td>
                <td><span class="pill ${item.case_status === 'Closed' ? 'g' : item.case_status === 'Draft' ? 'gray' : 'a'}">${item.case_status}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="IncidentModule.viewDetail('${item.report_id}')">View</button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="toolbar">
                <button class="btn btn-primary" onclick="HSEApp.navigateTo('incidents', 'add')">+ New Incident</button>
                <button class="btn btn-secondary" onclick="IncidentModule.showImportModal()">Import</button>
                <button class="btn btn-secondary" onclick="IncidentModule.exportData()">Export</button>
                <button class="btn btn-secondary" onclick="IncidentModule.refreshList()">Refresh</button>
            </div>

            <div class="filters">
                <input type="text" id="filter-search" placeholder="Search..." oninput="IncidentModule.applyFilters()">
                <select id="filter-severity" onchange="IncidentModule.applyFilters()">
                    <option value="">All Severities</option>
                    <option value="Fatality">Fatality</option>
                    <option value="LTI">LTI</option>
                    <option value="MTI">MTI</option>
                    <option value="First Aid">First Aid</option>
                    <option value="Near Miss">Near Miss</option>
                </select>
                <select id="filter-status" onchange="IncidentModule.applyFilters()">
                    <option value="">All Status</option>
                    <option value="Draft">Draft</option>
                    <option value="Submitted">Submitted</option>
                    <option value="Under Review">Under Review</option>
                    <option value="Approved">Approved</option>
                    <option value="Closed">Closed</option>
                </select>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Report ID</th>
                        <th>Date</th>
                        <th>Site</th>
                        <th>Location</th>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>

            <div class="pagination">
                <button class="btn btn-sm" ${currentPage <= 1 ? 'disabled' : ''} onclick="IncidentModule.goToPage(${currentPage - 1})">Previous</button>
                <span>Page ${data.page} of ${data.total_pages}</span>
                <button class="btn btn-sm" ${currentPage >= data.total_pages ? 'disabled' : ''} onclick="IncidentModule.goToPage(${currentPage + 1})">Next</button>
            </div>
        `;
    }

    function applyFilters() {
        const search = document.getElementById('filter-search')?.value || '';
        const severity = document.getElementById('filter-severity')?.value || '';
        const status = document.getElementById('filter-status')?.value || '';

        currentFilters = {};
        if (search) currentFilters.search = search;
        if (severity) currentFilters.severity = severity;
        if (status) currentFilters.case_status = status;

        currentPage = 1;
        loadList();
    }

    function goToPage(page) {
        currentPage = page;
        loadList();
    }

    function refreshList() {
        loadList();
    }

    async function exportData() {
        try {
            const startDate = document.getElementById('export-start')?.value || '2025-01-01';
            const endDate = document.getElementById('export-end')?.value || new Date().toISOString().split('T')[0];

            const response = await HSEApp.fetchWithAuth(`/api/incidents/export?start_date=${startDate}&end_date=${endDate}&format=csv`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `incidents_${startDate}_${endDate}.csv`;
                a.click();
                showToast('Export successful', 'success');
            }
        } catch (error) {
            showToast('Export failed', 'error');
        }
    }

    function showImportModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Import Incidents</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Upload a CSV file with incident data.</p>
                    <input type="file" id="import-file" accept=".csv" />
                    <div id="import-result"></div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="IncidentModule.doImport()">Import</button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async function doImport() {
        const fileInput = document.getElementById('import-file');
        if (!fileInput.files.length) {
            showToast('Please select a file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await HSEApp.fetchWithAuth('/api/incidents/import', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            document.getElementById('import-result').innerHTML = `
                <p>Success: ${result.success || 0}</p>
                <p>Failed: ${result.failed || 0}</p>
                ${result.errors?.length ? `<pre>${JSON.stringify(result.errors.slice(0, 5), null, 2)}</pre>` : ''}
            `;
        } catch (error) {
            showToast('Import failed', 'error');
        }
    }

    // =============================================
    // FORM VIEW
    // =============================================

    function showForm(mode) {
        const container = document.getElementById('incident-form-container');
        if (!container) return;

        const isEdit = mode === 'edit';
        const title = isEdit ? 'Edit Incident' : 'New Incident';

        container.innerHTML = `
            <div class="page-header">
                <h2>${title}</h2>
                <div class="page-actions">
                    <button class="btn btn-secondary" onclick="HSEApp.navigateTo('incidents', 'list')">Cancel</button>
                    <button class="btn btn-primary" onclick="IncidentModule.saveForm('${mode}')">Save</button>
                </div>
            </div>

            <form id="incident-form" class="form-container">
                <div class="form-section">
                    <h3>Basic Information</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Date *</label>
                            <input type="date" id="inc-report-date" required />
                        </div>
                        <div class="form-group">
                            <label>Time</label>
                            <input type="time" id="inc-report-time" />
                        </div>
                        <div class="form-group">
                            <label>Site *</label>
                            <select id="inc-site-id" required>
                                <option value="">Select Site</option>
                                <option value="SITE-A">Site Alpha Kutai</option>
                                <option value="SITE-A-C">Site Alpha Workshop</option>
                                <option value="SITE-B">Site Beta Balikpapan</option>
                                <option value="SITE-C">Site Gamma Samarinda</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Department</label>
                            <select id="inc-department-id">
                                <option value="">Select Department</option>
                                <option value="DEPT-MIN">Mining Operations</option>
                                <option value="DEPT-MNT">Mining Maintenance</option>
                                <option value="DEPT-EHS">EHS</option>
                                <option value="DEPT-PROC">Process Plant</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Shift</label>
                            <select id="inc-shift">
                                <option value="">Select Shift</option>
                                <option value="Morning">Morning</option>
                                <option value="Afternoon">Afternoon</option>
                                <option value="Night">Night</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Location *</label>
                            <input type="text" id="inc-location" required />
                        </div>
                        <div class="form-group">
                            <label>Category *</label>
                            <select id="inc-category" required>
                                <option value="">Select Category</option>
                                <option value="Injury">Injury</option>
                                <option value="Near Miss">Near Miss</option>
                                <option value="Property Damage">Property Damage</option>
                                <option value="Environmental">Environmental</option>
                                <option value="Security">Security</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Severity *</label>
                            <select id="inc-severity" required>
                                <option value="">Select Severity</option>
                                <option value="Fatality">Fatality</option>
                                <option value="LTI">LTI</option>
                                <option value="MTI">MTI</option>
                                <option value="First Aid">First Aid</option>
                                <option value="Near Miss">Near Miss</option>
                                <option value="Property Damage">Property Damage</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Incident Type *</label>
                            <input type="text" id="inc-incident-type" required />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Description *</label>
                            <textarea id="inc-description" rows="4" required></textarea>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Details</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>PIC</label>
                            <input type="text" id="inc-pic" />
                        </div>
                        <div class="form-group">
                            <label>Witness</label>
                            <input type="text" id="inc-witness" />
                        </div>
                        <div class="form-group">
                            <label>Injured Person</label>
                            <input type="text" id="inc-injured-person" />
                        </div>
                        <div class="form-group">
                            <label>Body Part</label>
                            <input type="text" id="inc-body-part" />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Lost Days</label>
                            <input type="number" id="inc-lost-days" value="0" min="0" />
                        </div>
                        <div class="form-group">
                            <label>PTW Required</label>
                            <input type="checkbox" id="inc-ptw-required" />
                        </div>
                        <div class="form-group">
                            <label>Investigation Required</label>
                            <input type="checkbox" id="inc-investigation-required" />
                        </div>
                        <div class="form-group">
                            <label>Investigation Due</label>
                            <input type="date" id="inc-investigation-due" />
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Actions & Root Cause</h3>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Immediate Action</label>
                            <textarea id="inc-immediate-action" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Root Cause</label>
                            <textarea id="inc-root-cause" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Corrective Action</label>
                            <textarea id="inc-corrective-action" rows="3"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        `;

        if (isEdit && editingId) {
            loadIncidentForEdit(editingId);
        }
    }

    async function loadIncidentForEdit(reportId) {
        try {
            const data = await HSEApp.get(`/api/incidents/${reportId}`);
            if (data) {
                document.getElementById('inc-report-date').value = data.report_date || '';
                document.getElementById('inc-report-time').value = data.report_time || '';
                document.getElementById('inc-site-id').value = data.site_id || '';
                document.getElementById('inc-department-id').value = data.department_id || '';
                document.getElementById('inc-shift').value = data.shift || '';
                document.getElementById('inc-location').value = data.location || '';
                document.getElementById('inc-category').value = data.category || '';
                document.getElementById('inc-severity').value = data.severity || '';
                document.getElementById('inc-incident-type').value = data.incident_type || '';
                document.getElementById('inc-description').value = data.description || '';
                document.getElementById('inc-immediate-action').value = data.immediate_action || '';
                document.getElementById('inc-root-cause').value = data.root_cause || '';
                document.getElementById('inc-corrective-action').value = data.corrective_action || '';
                document.getElementById('inc-pic').value = data.pic || '';
                document.getElementById('inc-witness').value = data.witness || '';
                document.getElementById('inc-injured-person').value = data.injured_person || '';
                document.getElementById('inc-body-part').value = data.body_part || '';
                document.getElementById('inc-lost-days').value = data.lost_days || 0;
                document.getElementById('inc-ptw-required').checked = data.ptw_required || false;
                document.getElementById('inc-investigation-required').checked = data.investigation_required || false;
                document.getElementById('inc-investigation-due').value = data.investigation_due || '';
            }
        } catch (error) {
            console.error('Failed to load incident:', error);
            showToast('Failed to load incident data', 'error');
        }
    }

    async function saveForm(mode) {
        const data = {
            report_date: document.getElementById('inc-report-date').value,
            report_time: document.getElementById('inc-report-time').value,
            site_id: document.getElementById('inc-site-id').value,
            department_id: document.getElementById('inc-department-id').value,
            shift: document.getElementById('inc-shift').value,
            location: document.getElementById('inc-location').value,
            category: document.getElementById('inc-category').value,
            severity: document.getElementById('inc-severity').value,
            incident_type: document.getElementById('inc-incident-type').value,
            description: document.getElementById('inc-description').value,
            immediate_action: document.getElementById('inc-immediate-action').value,
            root_cause: document.getElementById('inc-root-cause').value,
            corrective_action: document.getElementById('inc-corrective-action').value,
            pic: document.getElementById('inc-pic').value,
            witness: document.getElementById('inc-witness').value,
            injured_person: document.getElementById('inc-injured-person').value,
            body_part: document.getElementById('inc-body-part').value,
            lost_days: parseInt(document.getElementById('inc-lost-days').value) || 0,
            ptw_required: document.getElementById('inc-ptw-required').checked,
            investigation_required: document.getElementById('inc-investigation-required').checked,
            investigation_due: document.getElementById('inc-investigation-due').value,
        };

        try {
            let result;
            if (mode === 'edit' && editingId) {
                result = await HSEApp.put(`/api/incidents/${editingId}`, data);
            } else {
                result = await HSEApp.post('/api/incidents/', data);
            }

            if (result) {
                showToast(mode === 'edit' ? 'Incident updated' : 'Incident created', 'success');
                HSEApp.navigateTo('incidents', 'list');
            } else {
                showToast('Failed to save incident', 'error');
            }
        } catch (error) {
            console.error('Failed to save incident:', error);
            showToast('Failed to save incident', 'error');
        }
    }

    // =============================================
    // DETAIL VIEW
    // =============================================

    async function viewDetail(reportId) {
        editingId = reportId;
        const container = document.getElementById('incident-detail-container');
        if (!container) return;

        showLoading('incident-detail-container');

        try {
            const data = await HSEApp.get(`/api/incidents/${reportId}`);
            if (!data) {
                showToast('Incident not found', 'error');
                return;
            }

            const severityColors = {
                'Fatality': 'red', 'LTI': 'red', 'MTI': 'orange',
                'First Aid': 'yellow', 'Near Miss': 'blue', 'Property Damage': 'gray'
            };

            container.innerHTML = `
                <div class="page-header">
                    <h2>Incident Detail - ${data.report_id}</h2>
                    <div class="page-actions">
                        <button class="btn btn-secondary" onclick="HSEApp.navigateTo('incidents', 'list')">Back</button>
                        <button class="btn btn-primary" onclick="IncidentModule.editIncident('${data.report_id}')">Edit</button>
                    </div>
                </div>

                <div class="detail-grid">
                    <div class="card">
                        <h3>Basic Information</h3>
                        <div class="detail-row">
                            <span class="detail-label">Report ID:</span>
                            <span class="detail-value">${data.report_id}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span class="detail-value">${formatDate(data.report_date)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Site:</span>
                            <span class="detail-value">${data.site_id || '-'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Location:</span>
                            <span class="detail-value">${data.location || '-'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Severity:</span>
                            <span class="detail-value"><span class="pill ${severityColors[data.severity] || 'gray'}">${data.severity}</span></span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Status:</span>
                            <span class="detail-value"><span class="pill ${data.case_status === 'Closed' ? 'g' : data.case_status === 'Draft' ? 'gray' : 'a'}">${data.case_status}</span></span>
                        </div>
                    </div>

                    <div class="card">
                        <h3>Description</h3>
                        <p>${data.description || 'No description'}</p>
                    </div>

                    <div class="card">
                        <h3>Actions</h3>
                        <p><strong>Immediate Action:</strong> ${data.immediate_action || 'None'}</p>
                        <p><strong>Root Cause:</strong> ${data.root_cause || 'Not determined'}</p>
                        <p><strong>Corrective Action:</strong> ${data.corrective_action || 'None'}</p>
                    </div>

                    <div class="card">
                        <h3>Workflow History</h3>
                        <div id="workflow-history">
                            ${(data.workflow_history || []).map(wh => `
                                <div class="workflow-item">
                                    <span class="workflow-action">${wh.action}</span>
                                    <span class="workflow-from">${wh.from_status || 'N/A'}</span>
                                    <span class="workflow-arrow">→</span>
                                    <span class="workflow-to">${wh.to_status}</span>
                                    <span class="workflow-by">by ${wh.performed_by}</span>
                                    <span class="workflow-time">${formatDateTime(wh.performed_at)}</span>
                                </div>
                            `).join('') || '<p>No workflow history</p>'}
                        </div>
                    </div>
                </div>
            `;

            HSEApp.navigateTo('incidents', 'detail');
        } catch (error) {
            console.error('Failed to load incident detail:', error);
            showToast('Failed to load incident detail', 'error');
        }
    }

    function editIncident(reportId) {
        editingId = reportId;
        HSEApp.navigateTo('incidents', 'edit');
    }

    return {
        initStatic,
        init: initView,
        loadList,
        applyFilters,
        goToPage,
        refreshList,
        exportData,
        showImportModal,
        doImport,
        viewDetail,
        editIncident,
        saveForm
    };
})();
