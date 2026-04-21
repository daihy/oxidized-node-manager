// Dashboard JavaScript - Uses shared i18n.js for translations

// ============ Global State ============
let oxidizedStatus = {};
let allNodes = [];
let allCredentials = [];
let allModels = [];
let selectedVersions = [];

// ============ Utility Functions ============
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showAlert(message, type = 'success') {
    const alert = document.getElementById('alert');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    alert.style.display = 'block';
    setTimeout(() => alert.style.display = 'none', 5000);
}

// ============ UI Update ============
function updateUI() {
    // Global UI texts
    if (document.getElementById('page-title')) document.getElementById('page-title').textContent = t('title');
    if (document.getElementById('title')) document.getElementById('title').textContent = t('title');
    if (document.getElementById('subtitle')) document.getElementById('subtitle').textContent = t('subtitle');
    const langText = document.querySelector('#langBtn .lang-text');
    if (langText) langText.textContent = t('lang_switch');
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.textContent = t('logout_btn');

    // Tabs
    if (document.getElementById('tab-nodes-label')) document.getElementById('tab-nodes-label').textContent = t('tab_nodes');
    if (document.getElementById('tab-add-node-label')) document.getElementById('tab-add-node-label').textContent = t('tab_add_node');
    if (document.getElementById('tab-groups-label')) document.getElementById('tab-groups-label').textContent = t('tab_groups');
    if (document.getElementById('tab-import-label')) document.getElementById('tab-import-label').textContent = t('tab_import');
    if (document.getElementById('tab-users-label')) document.getElementById('tab-users-label').textContent = t('tab_users');
    if (document.getElementById('tab-credentials-label')) document.getElementById('tab-credentials-label').textContent = t('tab_credentials');
    if (document.getElementById('tab-models-label')) document.getElementById('tab-models-label').textContent = t('tab_models');
    if (document.getElementById('tab-config-label')) document.getElementById('tab-config-label').textContent = t('tab_config');

    // Nodes table headers
    if (document.getElementById('th-name')) document.getElementById('th-name').textContent = t('node_name');
    if (document.getElementById('th-ip')) document.getElementById('th-ip').textContent = t('ip_address');
    if (document.getElementById('th-model')) document.getElementById('th-model').textContent = t('device_model');
    if (document.getElementById('th-protocol')) document.getElementById('th-protocol').textContent = t('protocol');
    if (document.getElementById('th-port')) document.getElementById('th-port').textContent = t('port');
    if (document.getElementById('th-group')) document.getElementById('th-group').textContent = t('group');
    if (document.getElementById('th-oxidized-status')) document.getElementById('th-oxidized-status').textContent = t('backup_status');
    if (document.getElementById('th-oxidized-last')) document.getElementById('th-oxidized-last').textContent = t('last_backup');
    if (document.getElementById('th-action')) document.getElementById('th-action').textContent = t('action');

    // Groups table headers
    if (document.getElementById('th-grp-id')) document.getElementById('th-grp-id').textContent = t('grp_id');
    if (document.getElementById('th-grp-name')) document.getElementById('th-grp-name').textContent = t('grp_name');
    if (document.getElementById('th-grp-desc')) document.getElementById('th-grp-desc').textContent = t('grp_description');
    if (document.getElementById('th-grp-created')) document.getElementById('th-grp-created').textContent = t('grp_created');
    if (document.getElementById('th-grp-action')) document.getElementById('th-grp-action').textContent = t('grp_action');

    // Credentials headers
    if (document.getElementById('th-cred-enable')) document.getElementById('th-cred-enable').textContent = t('cred_enable');
    if (document.getElementById('th-cred-label')) document.getElementById('th-cred-label').textContent = t('cred_label');
    if (document.getElementById('th-cred-username')) document.getElementById('th-cred-username').textContent = t('cred_username');
    if (document.getElementById('th-cred-description')) document.getElementById('th-cred-description').textContent = t('cred_description');

    // Version History headers
    if (document.getElementById('th-version-number')) document.getElementById('th-version-number').textContent = t('cfg_version_number');
    if (document.getElementById('th-version-time')) document.getElementById('th-version-time').textContent = t('cfg_version_time');
    if (document.getElementById('th-version-action')) document.getElementById('th-version-action').textContent = t('cfg_version_action');

    // Users headers
    if (document.getElementById('th-user-username')) document.getElementById('th-user-username').textContent = t('user_username');
    if (document.getElementById('th-user-created')) document.getElementById('th-user-created').textContent = t('created');
    if (document.getElementById('th-user-action')) document.getElementById('th-user-action').textContent = t('user_action');

    // Modals titles and labels (dynamic via JS)
    const groupModalTitle = document.getElementById('group-modal-title');
    if (groupModalTitle) groupModalTitle.textContent = t('grp_add_title');
    const editTitle = document.getElementById('edit-title');
    if (editTitle) editTitle.textContent = t('edit_node_title') || editTitle.textContent;
    const changePwdTitle = document.getElementById('change-pwd-title');
    if (changePwdTitle) changePwdTitle.textContent = t('change_password');
    const addUserTitle = document.getElementById('add-user-title');
    if (addUserTitle) addUserTitle.textContent = t('add_user_title');
    const addCredTitle = document.getElementById('add-cred-title');
    if (addCredTitle) addCredTitle.textContent = t('add_credential_title');
    const editCredTitle = document.getElementById('edit-cred-title');
    if (editCredTitle) editCredTitle.textContent = t('edit_credential_title');
    const viewConfigTitle = document.getElementById('view-config-title');
    if (viewConfigTitle) viewConfigTitle.textContent = t('view_config_title');
    const versionHistoryTitle = document.getElementById('version-history-title');
    if (versionHistoryTitle) versionHistoryTitle.textContent = t('version_history_title');
    const diffTitle = document.getElementById('diff-title');
    if (diffTitle) diffTitle.textContent = t('compare_versions');

    // Diff legend labels
    if (document.getElementById('diff-old-version-label')) document.getElementById('diff-old-version-label').textContent = t('diff_old_version');
    if (document.getElementById('diff-new-version-label')) document.getElementById('diff-new-version-label').textContent = t('diff_new_version');

    // Backup interval modal
    const backupIntervalTitle = document.getElementById('backup-interval-title');
    if (backupIntervalTitle) backupIntervalTitle.textContent = t('backup_interval_title');

    // Placeholders and form labels (nodes, credentials, models, etc.)
    const nodeSearch = document.getElementById('nodeSearch');
    if (nodeSearch) nodeSearch.placeholder = t('node_search');
    const modelSearch = document.getElementById('modelSearch');
    if (modelSearch) modelSearch.placeholder = t('model_search_placeholder');
    const credSearch = document.getElementById('credSearch');
    if (credSearch) credSearch.placeholder = t('cred_search');
    const csvContent = document.getElementById('csvContent');
    if (csvContent) csvContent.placeholder = t('csv_placeholder');
    const labelCsv = document.getElementById('label-csv');
    if (labelCsv) labelCsv.textContent = t('paste_csv_label');
    const csvFormatLabel = document.getElementById('csv-format-label');
    if (csvFormatLabel) csvFormatLabel.textContent = t('csv_format_label');
    const csvExampleLabel = document.getElementById('csv-example-label');
    if (csvExampleLabel) csvExampleLabel.textContent = t('csv_example_label');

    // Node add form labels
    if (document.getElementById('label-name')) document.getElementById('label-name').textContent = t('node_name');
    if (document.getElementById('label-ip')) document.getElementById('label-ip').textContent = t('ip_address');
    if (document.getElementById('label-model')) document.getElementById('label-model').textContent = t('device_model');
    if (document.getElementById('label-protocol')) document.getElementById('label-protocol').textContent = t('protocol');
    if (document.getElementById('label-group')) document.getElementById('label-group').textContent = t('group');
    if (document.getElementById('label-port')) document.getElementById('label-port').textContent = t('port');
    if (document.getElementById('label-credential')) document.getElementById('label-credential').textContent = t('label_credential_node');
    if (document.getElementById('label-username')) document.getElementById('label-username').textContent = t('label_username');
    if (document.getElementById('label-password')) document.getElementById('label-password').textContent = t('label_password');

    // Group modal labels
    if (document.getElementById('grp-name-label')) document.getElementById('grp-name-label').textContent = t('grp_name_label');
    if (document.getElementById('grp-desc-label')) document.getElementById('grp-desc-label').textContent = t('grp_desc_label');
    if (document.getElementById('grp-save')) document.getElementById('grp-save').textContent = t('save');
    if (document.getElementById('grp-cancel')) document.getElementById('grp-cancel').textContent = t('cancel');

    // Re-apply role-based visibility after language change
    if (window.currentUserRole !== undefined) {
        applyRoleBasedVisibility();
    }
}

// ============ Language Switching ============
function switchLanguage() {
    currentLang = currentLang === 'en' ? 'zh' : 'en';
    localStorage.setItem('lang', currentLang);
    updateUI();
    refreshNodes();
    loadUsers();
}

// ============ Tab Navigation ============
function switchTab(tabName, ev) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    (ev || window.event).currentTarget.classList.add('active');

    if (tabName === 'users') {
        loadUsers();
    }
    if (tabName === 'models') {
        loadModels();
    }
    if (tabName === 'credentials') {
        loadCredentials();
    }
    if (tabName === 'add-node') {
        loadModelsToSelect('nodeModel');
        loadCredentialsToSelect('nodeCredential');
        loadGroupsToSelect('nodeGroup');
    }
    if (tabName === 'groups') {
        loadGroups();
    }
}

// ============ Logout ============
function logout() {
    if (confirm(t('confirm_logout') || 'Are you sure to logout?')) {
        window.location.href = '/api/logout';
    }
}

// ============ Password Toggle ============
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = event.target;
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '👁️‍🗨️';
    } else {
        input.type = 'password';
        button.textContent = '👁️';
    }
}

// ============ Node Port Auto-Update ============
function updateNodePort() {
    const protocol = document.getElementById('nodeProtocol').value;
    const portInput = document.getElementById('nodePort');
    portInput.value = protocol === 'ssh' ? '32410' : '23';
}

function updateEditNodePort() {
    const protocol = document.getElementById('editNodeProtocol').value;
    const portInput = document.getElementById('editNodePort');
    portInput.value = protocol === 'ssh' ? '32410' : '23';
}

// ============ Credential Auto-Fill ============
function onCredentialChange() {
    const credId = document.getElementById('nodeCredential').value;
    if (!credId) return;
    const cred = allCredentials.find(c => c.id == credId);
    if (cred) {
        document.getElementById('nodeUsername').value = cred.username || '';
        document.getElementById('nodePassword').value = cred.password || '';
    }
}

function onEditCredentialChange() {
    const credId = document.getElementById('editNodeCredential').value;
    if (!credId) return;
    const cred = allCredentials.find(c => c.id == credId);
    if (cred) {
        document.getElementById('editNodeUsername').value = cred.username || '';
        document.getElementById('editNodePassword').value = cred.password || '';
    }
}

// ============ Oxidized Status ============
function refreshOxidizedStatus() {
    fetch('/api/oxidized/status').then(r => r.json()).then(data => {
        oxidizedStatus = {};
        if (Array.isArray(data)) {
            data.forEach(node => {
                oxidizedStatus[node.name] = node;
            });
        }
        refreshNodes();
    }).catch(err => {
        console.error('Failed to fetch Oxidized status:', err);
        refreshNodes();
    });
}

function restartOxidizedContainer() {
    if (!confirm('Restart Oxidized container? This will interrupt current backups.')) return;
    showAlert('Restarting Oxidized container...', 'info');
    fetch('/api/oxidized/restart', {method: 'POST'}).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Oxidized container restarted successfully');
            setTimeout(refreshOxidizedStatus, 3000);
        } else {
            showAlert('Failed to restart Oxidized: ' + (data.error || 'Unknown error'), 'error');
        }
    }).catch(err => {
        showAlert('Error restarting Oxidized: ' + err.message, 'error');
    });
}

function getOxidizedLastSync(status) {
    if (!status || !status.last || !status.last.end) return 'Never';
    try {
        return new Date(status.last.end).toLocaleString();
    } catch(e) {
        return status.last.end;
    }
}

function getOxidizedStatusBadge(nodeName) {
    const status = oxidizedStatus[nodeName];
    if (!status) {
        return '<span style="color: #999;">Not in Oxidized</span>';
    }
    const lastSync = getOxidizedLastSync(status);
    const statusText = status.status === 'success' ? '<span style="color: #28a745;">✓ Success</span>' :
                      status.status === 'failed' ? '<span style="color: #dc3545;">✗ Failed</span>' :
                      '<span style="color: #ffc107;">⏳ ' + (status.status || 'Unknown') + '</span>';
    return `<div>${statusText}</div><div style="font-size: 11px; color: #666;">${lastSync}</div>`;
}

// ============ Node Filtering & Rendering ============
function filterNodes() {
    const searchText = document.getElementById('nodeSearch').value.toLowerCase();
    const groupFilter = document.getElementById('nodeGroupFilter').value;

    const filtered = allNodes.filter(node => {
        const matchesSearch = !searchText ||
            (node.name && node.name.toLowerCase().includes(searchText)) ||
            (node.ip && node.ip.toLowerCase().includes(searchText)) ||
            (node.model && node.model.toLowerCase().includes(searchText));
        const matchesGroup = !groupFilter || String(node.group_id) === String(groupFilter);
        return matchesSearch && matchesGroup;
    });

    renderNodesTable(filtered);
}

function renderNodesTable(nodes) {
    const tbody = document.getElementById('nodesList');
    if (nodes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;">No matching nodes</td></tr>`;
        return;
    }
    tbody.innerHTML = nodes.map(node => `
        <tr>
            <td>${escapeHtml(node.name)}</td>
            <td>${escapeHtml(node.ip)}</td>
            <td>${escapeHtml(node.model || '-')}</td>
            <td>${escapeHtml(node.protocol || '-')}</td>
            <td>${node.port || '-'}</td>
            <td>${node.group_name ? '<span style="background:#e3f2fd;padding:2px 8px;border-radius:12px;font-size:12px;">' + escapeHtml(node.group_name) + '</span>' : '<span style="color:#999;">-</span>'}</td>
            <td>${getOxidizedStatusBadge(node.name)}</td>
            <td>${getOxidizedLastSync(oxidizedStatus[node.name]) || '-'}</td>
            <td>
                <div class="action-btn-group">
                    <button class="action-btn action-btn-edit" onclick="openEditModal('${escapeHtml(node.name)}')" title="Edit">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                    </button>
                    <button class="action-btn action-btn-view" onclick="viewConfig('${escapeHtml(node.name)}')" title="View Config">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                    </button>
                    <button class="action-btn action-btn-history" onclick="viewVersionHistory('${escapeHtml(node.name)}')" title="Version History">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
                    </button>
                    <button class="action-btn action-btn-backup" onclick="triggerBackup('${escapeHtml(node.name)}')" title="Trigger Backup">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
                    </button>
                    <button class="action-btn action-btn-delete" onclick="deleteNode('${escapeHtml(node.name)}')" title="Delete">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function refreshNodes() {
    document.getElementById('nodesList').innerHTML = `<tr><td colspan="9" style="text-align:center;">${t('loading')}</td></tr>`;
    fetch('/api/nodes').then(r => r.json()).then(nodes => {
        allNodes = nodes;
        // Populate group filter dropdown
        const groupFilter = document.getElementById('nodeGroupFilter');
        const groupMap = new Map();
        nodes.forEach(n => {
            if (n.group_id != null && n.group_name && String(n.group_name).trim()) {
                if (!groupMap.has(n.group_id)) {
                    groupMap.set(n.group_id, n.group_name);
                }
            }
        });
        const uniqueGroups = [...groupMap.entries()];
        const currentFilter = groupFilter.value;
        groupFilter.innerHTML = '<option value="">All Groups</option>' +
            uniqueGroups.map(([id, name]) => `<option value="${id}">${escapeHtml(name)}</option>`)
                .join('');
        groupFilter.value = currentFilter;
        filterNodes();
    });
}

// ============ Oxidized Config Functions ============
function viewConfig(nodeName) {
    document.getElementById('view-config-node-name').textContent = nodeName;
    document.getElementById('view-config-status').innerHTML = '<span class="skeleton skeleton-inline" style="width: 120px;"></span>';
    document.getElementById('viewConfigContent').value = '';
    document.getElementById('viewConfigModal').classList.add('show');

    fetch(`/api/oxidized/node/${nodeName}/config`).then(r => r.json()).then(data => {
        if (data.config) {
            document.getElementById('viewConfigContent').value = data.config;
            document.getElementById('view-config-status').textContent = '✓ Config loaded';
        } else {
            document.getElementById('view-config-status').textContent = '✗ Failed to load config';
        }
    }).catch(err => {
        document.getElementById('view-config-status').textContent = '✗ Error: ' + err.message;
    });
}

function closeViewConfigModal() {
    document.getElementById('viewConfigModal').classList.remove('show');
}

function copyConfig() {
    const config = document.getElementById('viewConfigContent').value;
    navigator.clipboard.writeText(config).then(() => {
        showAlert('Config copied to clipboard');
    }).catch(() => {
        showAlert('Failed to copy config', 'error');
    });
}

// ============ Oxidized Version History ============
function viewVersionHistory(nodeName) {
    document.getElementById('version-history-node-name').textContent = nodeName;
    document.getElementById('versionHistoryList').innerHTML = `
        <div class="skeleton-row"><span class="skeleton skeleton-inline" style="width: 250px;"></span></div>
        <div class="skeleton-row"><span class="skeleton skeleton-inline" style="width: 250px;"></span></div>
        <div class="skeleton-row"><span class="skeleton skeleton-inline" style="width: 250px;"></span></div>
    `;
    document.getElementById('versionDetailContent').innerHTML = '<div style="padding: 40px; text-align: center;"><span class="skeleton skeleton-inline" style="width: 200px;"></span></div>';
    selectedVersions = [];
    document.getElementById('versionHistoryModal').classList.add('show');

    fetch(`/api/oxidized/node/${nodeName}/history`).then(r => r.json()).then(data => {
        if (Array.isArray(data) && data.length > 0) {
            document.getElementById('versionHistoryList').innerHTML = data.map((v, idx) => {
                // Convert ISO date string "2026-04-21 07:25:45 +0000" to Unix epoch seconds
                const dateStr = v.time || v.date || '';
                const epochSecs = dateStr ? Math.round(new Date(dateStr).getTime() / 1000) : 0;
                return `
                <div style="display: flex; align-items: center; padding: 8px; border-bottom: 1px solid #eee; gap: 8px; flex-wrap: nowrap;">
                    <input type="checkbox" class="version-checkbox" data-oid="${v.oid}" data-epoch="${epochSecs}" data-num="${data.length - idx}" style="margin: 0; width: 16px; flex-shrink: 0;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Version ${data.length - idx} - ${v.date || v.timestamp || 'Unknown date'}</div>
                    </div>
                    <button class="btn" style="padding:5px 10px;font-size:11px; flex-shrink: 0;" onclick="viewVersionDetail('${nodeName}', '${v.oid}', '${epochSecs}')">View</button>
                </div>
            `}).join('');
        } else {
            document.getElementById('versionHistoryList').innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No version history found</div>';
        }
    }).catch(err => {
        document.getElementById('versionHistoryList').innerHTML = '<div style="padding: 20px; text-align: center; color: #dc3545;">Error: ' + err.message + '</div>';
    });
}

function viewVersionDetail(nodeName, oid, epoch) {
    fetch(`/api/oxidized/node/${nodeName}/version?oid=${encodeURIComponent(oid)}&epoch=${encodeURIComponent(epoch)}`).then(r => r.json()).then(data => {
        if (data.config) {
            document.getElementById('versionDetailContent').innerHTML = `
                <textarea readonly style="width: 100%; height: 280px; font-family: monospace; font-size: 12px;">${data.config}</textarea>
                <div style="margin-top: 10px;">
                    <button class="btn" onclick="copyVersionConfig()">📋 Copy</button>
                </div>
            `;
            window.currentVersionConfig = data.config;
        } else {
            document.getElementById('versionDetailContent').innerHTML = '<div style="color: #dc3545;">Failed to load version config</div>';
        }
    });
}

function copyVersionConfig() {
    if (window.currentVersionConfig) {
        navigator.clipboard.writeText(window.currentVersionConfig).then(() => {
            showAlert('Version config copied to clipboard');
        });
    }
}

function compareVersions() {
    const checkboxes = document.querySelectorAll('.version-checkbox:checked');
    if (checkboxes.length !== 2) {
        showAlert('Please select exactly 2 versions to compare', 'error');
        return;
    }
    const ep1 = parseInt(checkboxes[0].dataset.epoch) || 0;
    const ep2 = parseInt(checkboxes[1].dataset.epoch) || 0;
    const oid1 = checkboxes[0].dataset.oid;
    const oid2 = checkboxes[1].dataset.oid;
    const epoch1 = checkboxes[0].dataset.epoch;
    const epoch2 = checkboxes[1].dataset.epoch;
    const nodeName = document.getElementById('version-history-node-name').textContent;

    let oldOid, newOid, oldEpoch, newEpoch;
    if (ep1 < ep2) {
        oldOid = oid1; newOid = oid2;
        oldEpoch = epoch1; newEpoch = epoch2;
    } else {
        oldOid = oid2; newOid = oid1;
        oldEpoch = epoch2; newEpoch = epoch1;
    }

    closeVersionHistoryModal();
    showDiff(nodeName, oldOid, newOid, oldEpoch, newEpoch);
}

function showDiff(nodeName, oid1, oid2, epoch1, epoch2) {
    document.getElementById('diff-node-name').textContent = nodeName;
    document.getElementById('diff-versions').textContent = 'Left = Older | Right = Newer';
    document.getElementById('diff-old-content').innerHTML = '<div style="padding: 40px; text-align: center;"><span class="skeleton skeleton-inline" style="width: 150px;"></span></div>';
    document.getElementById('diff-new-content').innerHTML = '<div style="padding: 40px; text-align: center;"><span class="skeleton skeleton-inline" style="width: 150px;"></span></div>';
    document.getElementById('diffModal').classList.add('show');
    window.diffMode = 'all';
    document.getElementById('btn-toggle-mode').textContent = 'Show: All';

    window.diffNodeName = nodeName;
    window.diffOid1 = oid1;
    window.diffOid2 = oid2;

    fetch(`/api/oxidized/node/${nodeName}/diff?oid1=${encodeURIComponent(oid1)}&oid2=${encodeURIComponent(oid2)}&epoch1=${encodeURIComponent(epoch1 || '')}&epoch2=${encodeURIComponent(epoch2 || '')}`).then(r => r.json()).then(data => {
        if (data.aligned_lines && data.aligned_lines.length > 0) {
            window.diffData = data.aligned_lines;
            window.diffStats = data.stats;
            renderSplitDiff(data.aligned_lines, data.stats);
        } else {
            document.getElementById('diff-old-content').innerHTML = '<div style="padding: 20px; color: #666;">No differences found.</div>';
            document.getElementById('diff-new-content').innerHTML = '<div style="padding: 20px; color: #666;">No differences found.</div>';
        }
    }).catch(err => {
        document.getElementById('diff-old-content').innerHTML = '<div style="padding: 20px; color: #dc3545;">Error: ' + err.message + '</div>';
        document.getElementById('diff-new-content').innerHTML = '<div style="padding: 20px; color: #dc3545;">Error: ' + err.message + '</div>';
    });
}

function toggleDiffMode() {
    if (!window.diffData) return;
    window.diffMode = window.diffMode === 'all' ? 'diff' : 'all';
    document.getElementById('btn-toggle-mode').textContent = window.diffMode === 'all' ? 'Show: All' : 'Show: Diff Only';
    renderSplitDiff(window.diffData, window.diffStats);
}

function syncScroll(source, targetId) {
    let isScrolling = false;
    if (isScrolling) return;
    isScrolling = true;
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollTop = source.scrollTop;
        target.scrollLeft = source.scrollLeft;
    }
    requestAnimationFrame(() => { isScrolling = false; });
}

function renderSplitDiff(lines, stats) {
    let oldHtml = '';
    let newHtml = '';
    let modifiedPair = null;
    const mode = window.diffMode || 'all';

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        if (line.type === 'equal') {
            if (mode === 'diff') continue;
            oldHtml += `<div style="display: flex; min-height: 22px;">
                <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;">${line.old_line}</span>
                <span style="padding: 0 8px; white-space: pre; flex: 1; background: #e8e8e8;">${escapeHtml(line.old_content)}</span>
            </div>`;
            newHtml += `<div style="display: flex; min-height: 22px;">
                <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;">${line.new_line}</span>
                <span style="padding: 0 8px; white-space: pre; flex: 1; background: #e8e8e8;">${escapeHtml(line.new_content)}</span>
            </div>`;
        } else if (line.type === 'delete') {
            const bgColor = '#ffcdd2';
            oldHtml += `<div style="display: flex; min-height: 22px; background: ${bgColor};">
                <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;">${line.old_line || ''}</span>
                <span style="padding: 0 8px; white-space: pre; flex: 1;">${escapeHtml(line.old_content)}</span>
            </div>`;
            if (mode === 'all') {
                newHtml += `<div style="display: flex; min-height: 22px; background: ${bgColor}; opacity: 0.4;">
                    <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;"></span>
                    <span style="padding: 0 8px; white-space: pre; flex: 1;"></span>
                </div>`;
            }
        } else if (line.type === 'insert') {
            const bgColor = '#c8e6c9';
            if (modifiedPair === null && i > 0 && lines[i-1].type === 'delete') {
                modifiedPair = i;
            }
            const bg = modifiedPair !== null ? '#fff9c4' : bgColor;
            newHtml += `<div style="display: flex; min-height: 22px; background: ${bg};">
                <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;">${line.new_line || ''}</span>
                <span style="padding: 0 8px; white-space: pre; flex: 1;">${escapeHtml(line.new_content)}</span>
            </div>`;
            if (mode === 'all') {
                oldHtml += `<div style="display: flex; min-height: 22px; background: ${bg}; opacity: 0.4;">
                    <span style="width: 50px; padding: 0 8px; color: #888; text-align: right; user-select: none; flex-shrink: 0; border-right: 1px solid #ddd;"></span>
                    <span style="padding: 0 8px; white-space: pre; flex: 1;"></span>
                </div>`;
            }
        }

        if (modifiedPair !== null && i - modifiedPair > 0) {
            modifiedPair = null;
        }
    }

    document.getElementById('diff-old-content').innerHTML = oldHtml || '<div style="padding: 20px; color: #666;">No content</div>';
    document.getElementById('diff-new-content').innerHTML = newHtml || '<div style="padding: 20px; color: #666;">No content</div>';

    if (stats) {
        if (mode === 'diff') {
            document.getElementById('diff-old-count').textContent = `${stats.delete} removed`;
            document.getElementById('diff-new-count').textContent = `${stats.insert} added`;
        } else {
            document.getElementById('diff-old-count').textContent = `${stats.equal} same | ${stats.delete} removed`;
            document.getElementById('diff-new-count').textContent = `${stats.equal} same | ${stats.insert} added`;
        }
    }
}

function closeVersionHistoryModal() {
    document.getElementById('versionHistoryModal').classList.remove('show');
}

function closeDiffModal() {
    document.getElementById('diffModal').classList.remove('show');
}

// ============ Backup Interval ============
function openBackupIntervalModal() {
    fetch('/api/oxidized/interval').then(r => r.json()).then(data => {
        document.getElementById('backupIntervalMinutes').value = data.interval_minutes;
        document.getElementById('backupIntervalModal').classList.add('show');
    }).catch(err => {
        showAlert('Failed to load current interval', 'error');
    });
}

function closeBackupIntervalModal() {
    document.getElementById('backupIntervalModal').classList.remove('show');
}

function saveBackupInterval(e) {
    e.preventDefault();
    const minutes = parseInt(document.getElementById('backupIntervalMinutes').value);

    fetch('/api/oxidized/interval', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({minutes: minutes})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(`Backup interval updated to ${minutes} minutes`);
            closeBackupIntervalModal();
            refreshOxidizedInfo();
        } else {
            showAlert('Failed to update interval: ' + (data.error || 'Unknown error'), 'error');
        }
    }).catch(err => {
        showAlert('Failed to update interval: ' + err.message, 'error');
    });
}

// ============ Trigger Backup ============
function triggerBackup(nodeName) {
    if (!confirm(`Trigger backup for ${nodeName}?`)) return;

    showAlert(`Triggering backup for ${nodeName}...`, 'info');
    fetch(`/api/oxidized/node/${nodeName}/backup`, {method: 'POST'}).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(`Backup triggered for ${nodeName}`);
            setTimeout(refreshOxidizedStatus, 2000);
        } else {
            showAlert(`Failed to trigger backup: ${data.error}`, 'error');
        }
    }).catch(err => {
        showAlert(`Error: ${err.message}`, 'error');
    });
}

// ============ Node CRUD ============
function openEditModal(name) {
    Promise.all([
        fetch('/api/credentials').then(r => r.json()),
        fetch('/api/models').then(r => r.json()),
        fetch('/api/groups').then(r => r.json())
    ]).then(([creds, models, groupsData]) => {
        allCredentials = creds;

        const credSelect = document.getElementById('editNodeCredential');
        credSelect.innerHTML = '<option value="">Select credential</option>';
        creds.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = `${c.label} (${c.username})`;
            credSelect.appendChild(opt);
        });

        const modelSelect = document.getElementById('editNodeModel');
        modelSelect.innerHTML = '<option value="">Select device model</option>';
        models.filter(m => m.enabled).forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.id} - ${m.name}`;
            modelSelect.appendChild(opt);
        });

        const groupSelect = document.getElementById('editNodeGroup');
        groupSelect.innerHTML = '<option value="">No Group</option>';
        groupsData.groups.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.id;
            opt.textContent = g.name;
            groupSelect.appendChild(opt);
        });

        return fetch(`/api/nodes/${name}`);
    }).then(r => r.json()).then(node => {
        document.getElementById('editNodeName').value = node.name;
        document.getElementById('editNodeIp').value = node.ip;
        document.getElementById('editNodeModel').value = node.model;
        document.getElementById('editNodeProtocol').value = node.protocol || 'ssh';
        document.getElementById('editNodePort').value = node.port || '32410';
        document.getElementById('editNodeUsername').value = node.username || '';
        document.getElementById('editNodePassword').value = node.password || '';
        document.getElementById('editNodeGroup').value = node.group_id || '';
        document.getElementById('editModal').classList.add('show');
    });
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('show');
}

function updateNode(e) {
    e.preventDefault();
    const nodeName = document.getElementById('editNodeName').value;
    const groupId = document.getElementById('editNodeGroup').value;
    const node = {
        name: nodeName,
        ip: document.getElementById('editNodeIp').value,
        model: document.getElementById('editNodeModel').value,
        protocol: document.getElementById('editNodeProtocol').value,
        port: document.getElementById('editNodePort').value,
        username: document.getElementById('editNodeUsername').value,
        password: document.getElementById('editNodePassword').value,
        group_id: groupId ? parseInt(groupId) : null
    };
    fetch(`/api/nodes/${nodeName}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(node)})
        .then(r => r.json()).then(data => {
            if (data.success) {
                showAlert(t('success_update_node'));
                closeEditModal();
                refreshNodes();
            }
        });
}

function addNode(e) {
    e.preventDefault();
    const groupId = document.getElementById('nodeGroup').value;
    const node = {
        name: document.getElementById('nodeName').value,
        ip: document.getElementById('nodeIp').value,
        model: document.getElementById('nodeModel').value,
        protocol: document.getElementById('nodeProtocol').value,
        port: document.getElementById('nodePort').value,
        username: document.getElementById('nodeUsername').value,
        password: document.getElementById('nodePassword').value,
        group_id: groupId ? parseInt(groupId) : null
    };
    fetch('/api/nodes', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(node)})
        .then(r => r.json()).then(data => {
            if (data.success) {
                showAlert(t('success_add_node'));
                e.target.reset();
                refreshNodes();
            }
        });
}

function deleteNode(name) {
    if (confirm(t('confirm_delete'))) {
        fetch(`/api/nodes/${name}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert(t('success_delete_node'));
                refreshNodes();
            }
        });
    }
}

function importNodes(e) {
    e.preventDefault();
    const csv = document.getElementById('csvContent').value;
    fetch('/api/import', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({csv: csv})})
        .then(r => r.json()).then(data => {
            if (data.success) {
                showAlert('Successfully imported ' + data.count + ' nodes');
                document.getElementById('csvContent').value = '';
                refreshNodes();
            }
        });
}

// ============ Users ============
function loadUsers() {
    fetch('/api/users').then(r => r.json()).then(users => {
        const tbody = document.getElementById('usersList');
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3">${t('no_data') || 'No users'}</td></tr>`;
            return;
        }
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${escapeHtml(user.username)}</td>
                <td>${user.created || t('no_data')}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn" style="padding:5px 10px;font-size:12px;" onclick="openUserChangePasswordModal('${user.username}')">${t('change_password')}</button>
                        <button class="btn btn-danger" style="padding:5px 10px;font-size:12px;" onclick="deleteUser('${user.username}')">${t('delete')}</button>
                    </div>
                </td>
            </tr>
        `).join('');
    });
}

function openAddUserModal() {
    document.getElementById('addUserModal').classList.add('show');
}

function closeAddUserModal() {
    document.getElementById('addUserModal').classList.remove('show');
}

function handleAddUser(e) {
    e.preventDefault();
    const username = document.getElementById('addUserUsername').value;
    const password = document.getElementById('addUserPassword').value;

    if (password.length < 6) {
        showAlert(t('error_password_short'), 'error');
        return;
    }

    fetch('/api/users', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(t('success_add_user'));
            closeAddUserModal();
            document.getElementById('addUserUsername').value = '';
            document.getElementById('addUserPassword').value = '';
            loadUsers();
        } else {
            showAlert(data.error, 'error');
        }
    });
}

function deleteUser(username) {
    if (confirm(t('confirm_delete'))) {
        fetch(`/api/users/${username}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert(t('success_delete_user'));
                loadUsers();
            }
        });
    }
}

function openUserChangePasswordModal(username) {
    document.getElementById('userChangePasswordUsername').value = username;
    document.getElementById('userChangePasswordNew').value = '';
    document.getElementById('userChangePasswordConfirm').value = '';
    document.getElementById('userChangePasswordAlert').style.display = 'none';
    document.getElementById('userChangePasswordModal').classList.add('show');
}

function closeUserChangePasswordModal() {
    document.getElementById('userChangePasswordModal').classList.remove('show');
}

function handleUserChangePassword(e) {
    e.preventDefault();
    const username = document.getElementById('userChangePasswordUsername').value;
    const newPass = document.getElementById('userChangePasswordNew').value;
    const confirm = document.getElementById('userChangePasswordConfirm').value;
    const alertDiv = document.getElementById('userChangePasswordAlert');

    if (newPass.length < 6) {
        alertDiv.className = 'alert error';
        alertDiv.textContent = t('error_password_short');
        alertDiv.style.display = 'block';
        return;
    }

    if (newPass !== confirm) {
        alertDiv.className = 'alert error';
        alertDiv.textContent = t('error_password_mismatch');
        alertDiv.style.display = 'block';
        return;
    }

    fetch('/api/users-admin-change-password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username, new_password: newPass})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(t('success_change_password'));
            closeUserChangePasswordModal();
            loadUsers();
        } else {
            alertDiv.className = 'alert error';
            alertDiv.textContent = data.error || 'Failed to change password';
            alertDiv.style.display = 'block';
        }
    });
}

// ============ Change Password (Self) ============
function openChangePasswordModal() {
    document.getElementById('changePasswordModal').classList.add('show');
}

function closeChangePasswordModal() {
    document.getElementById('changePasswordModal').classList.remove('show');
    document.getElementById('changePasswordCurrent').value = '';
    document.getElementById('changePasswordNew').value = '';
    document.getElementById('changePasswordConfirm').value = '';
}

function handleChangePassword(e) {
    e.preventDefault();
    const current = document.getElementById('changePasswordCurrent').value;
    const newPass = document.getElementById('changePasswordNew').value;
    const confirm = document.getElementById('changePasswordConfirm').value;

    if (newPass.length < 6) {
        showAlert(t('error_password_short'), 'error');
        return;
    }

    if (newPass !== confirm) {
        showAlert(t('error_password_mismatch'), 'error');
        return;
    }

    if (newPass === current) {
        showAlert(t('error_password_same'), 'error');
        return;
    }

    fetch('/api/change-password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({current_password: current, new_password: newPass})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(t('success_change_password'));
            closeChangePasswordModal();
        } else {
            showAlert(data.error, 'error');
        }
    });
}

// ============ Groups ============
function loadGroups() {
    fetch('/api/groups').then(r => r.json()).then(data => {
        const tbody = document.getElementById('groups-list');
        if (!tbody) return;
        if (data.groups.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No groups yet</td></tr>';
            return;
        }
        tbody.innerHTML = data.groups.map(g => `
            <tr>
                <td>${g.id}</td>
                <td>${escapeHtml(g.name)}</td>
                <td>${escapeHtml(g.description || '-')}</td>
                <td>${g.created || '-'}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn" style="padding:5px 10px;font-size:12px;" onclick="openEditGroupModal(${g.id}, '${escapeHtml(g.name)}', '${escapeHtml(g.description || '')}')">Edit</button>
                        <button class="btn btn-danger" style="padding:5px 10px;font-size:12px;" onclick="deleteGroup(${g.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    });
}

function openAddGroupModal() {
    document.getElementById('group-modal-title').textContent = t('grp_add_title');
    document.getElementById('grp-name-label').textContent = t('grp_name_label');
    document.getElementById('grp-desc-label').textContent = t('grp_desc_label');
    document.getElementById('groupDescription').placeholder = t('grp_optional_desc');
    document.getElementById('grp-save').textContent = t('grp_save');
    document.getElementById('grp-cancel').textContent = t('grp_cancel');
    document.getElementById('editGroupId').value = '';
    document.getElementById('groupName').value = '';
    document.getElementById('groupDescription').value = '';
    document.getElementById('groupModal').classList.add('show');
}

function openEditGroupModal(id, name, description) {
    document.getElementById('group-modal-title').textContent = t('grp_edit_title');
    document.getElementById('grp-name-label').textContent = t('grp_name_label');
    document.getElementById('grp-desc-label').textContent = t('grp_desc_label');
    document.getElementById('groupDescription').placeholder = t('grp_optional_desc');
    document.getElementById('grp-save').textContent = t('grp_save');
    document.getElementById('grp-cancel').textContent = t('grp_cancel');
    document.getElementById('editGroupId').value = id;
    document.getElementById('groupName').value = name;
    document.getElementById('groupDescription').value = description || '';
    document.getElementById('groupModal').classList.add('show');
}

function closeGroupModal() {
    document.getElementById('groupModal').classList.remove('show');
}

function saveGroup(e) {
    e.preventDefault();
    const id = document.getElementById('editGroupId').value;
    const name = document.getElementById('groupName').value.trim();
    const description = document.getElementById('groupDescription').value.trim();

    if (!name) {
        showAlert('Group name is required', 'error');
        return;
    }

    const payload = { name, description };
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/groups/${id}` : '/api/groups';

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    }).then(r => r.json()).then(data => {
        if (data.success || data.id) {
            showAlert(id ? 'Group updated' : 'Group created');
            closeGroupModal();
            loadGroups();
            loadGroupsToSelect('nodeGroup');
            loadGroupsToSelect('editNodeGroup');
        } else {
            showAlert(data.error || 'Failed to save group', 'error');
        }
    });
}

function deleteGroup(id) {
    if (confirm('Delete this group? Nodes in this group will become ungrouped.')) {
        fetch(`/api/groups/${id}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert('Group deleted');
                loadGroups();
                loadGroupsToSelect('nodeGroup');
                loadGroupsToSelect('editNodeGroup');
            } else {
                showAlert(data.error || 'Failed to delete group', 'error');
            }
        });
    }
}

// ============ Models ============
function loadModels() {
    fetch('/api/models').then(r => r.json()).then(models => {
        allModels = models;
        const tbody = document.getElementById('modelsList');
        tbody.innerHTML = models.map(m => `
            <tr>
                <td><input type="checkbox" id="model-${m.id}" value="${m.id}" ${m.enabled ? 'checked' : ''}></td>
                <td>${escapeHtml(m.name)}</td>
                <td><strong>${escapeHtml(m.id)}</strong></td>
            </tr>
        `).join('');
    });
}

function saveModels() {
    const enabled = [];
    allModels.forEach(m => {
        const checkbox = document.getElementById('model-' + m.id);
        if (checkbox && checkbox.checked) {
            enabled.push(m.id);
        }
    });
    fetch('/api/models', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({models: enabled})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert(t('success_save_models') || 'Models saved successfully');
        }
    });
}

function filterModels() {
    const searchText = document.getElementById('modelSearch').value.toLowerCase();
    const filteredModels = allModels.filter(m =>
        m.id.toLowerCase().includes(searchText) ||
        m.name.toLowerCase().includes(searchText)
    );
    const tbody = document.getElementById('modelsList');
    tbody.innerHTML = filteredModels.map(m => `
        <tr>
            <td><input type="checkbox" id="model-${m.id}" value="${m.id}" ${m.enabled ? 'checked' : ''}></td>
            <td>${escapeHtml(m.name)}</td>
            <td><strong>${escapeHtml(m.id)}</strong></td>
        </tr>
    `).join('');
}

function selectAllModels() {
    allModels.forEach(m => {
        const checkbox = document.getElementById('model-' + m.id);
        if (checkbox) checkbox.checked = true;
    });
}

function deselectAllModels() {
    allModels.forEach(m => {
        const checkbox = document.getElementById('model-' + m.id);
        if (checkbox) checkbox.checked = false;
    });
}

// ============ Credentials ============
function loadCredentials() {
    fetch('/api/credentials').then(r => r.json()).then(creds => {
        allCredentials = creds;
        renderCredentialsList(creds);
    });
}

function renderCredentialsList(creds) {
    const tbody = document.getElementById('credentialsList');
    tbody.innerHTML = creds.map(c => `
        <tr>
            <td><input type="checkbox" id="cred-${c.id}" value="${c.id}" checked></td>
            <td>${escapeHtml(c.label)}</td>
            <td>${escapeHtml(c.username)}</td>
            <td>${escapeHtml(c.description || '')}</td>
            <td>
                <div class="btn-group">
                    <button class="btn" style="padding:5px 10px;font-size:12px;" onclick="openEditCredentialModal('${c.id}')">${t('edit')}</button>
                    <button class="btn btn-danger" style="padding:5px 10px;font-size:12px;" onclick="deleteCredential('${c.id}')">${t('delete')}</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function saveCredentials() {
    // Credentials are saved via individual Add/Edit modals, not a global save.
    // This button exists in the credentials tab header for discoverability.
    // Open the Add Credential modal so user can fill and submit the form.
    openAddCredentialModal();
}

function filterCredentials() {
    const searchText = document.getElementById('credSearch').value.toLowerCase();
    const filtered = allCredentials.filter(c =>
        c.label.toLowerCase().includes(searchText) ||
        c.username.toLowerCase().includes(searchText) ||
        (c.description && c.description.toLowerCase().includes(searchText))
    );
    renderCredentialsList(filtered);
}

function openAddCredentialModal() {
    document.getElementById('addCredId').value = '';
    document.getElementById('addCredLabel').value = '';
    document.getElementById('addCredUsername').value = '';
    document.getElementById('addCredPassword').value = '';
    document.getElementById('addCredEnablePassword').value = '';
    document.getElementById('addCredDescription').value = '';
    document.getElementById('addCredentialModal').classList.add('show');
}

function closeAddCredentialModal() {
    document.getElementById('addCredentialModal').classList.remove('show');
}

function handleAddCredential(e) {
    e.preventDefault();
    const cred = {
        id: document.getElementById('addCredId').value || '',
        label: document.getElementById('addCredLabel').value,
        username: document.getElementById('addCredUsername').value,
        password: document.getElementById('addCredPassword').value,
        enable_password: document.getElementById('addCredEnablePassword').value,
        description: document.getElementById('addCredDescription').value
    };
    fetch('/api/credentials', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(cred)
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Credential added successfully');
            closeAddCredentialModal();
            loadCredentials();
        } else {
            showAlert(data.error || 'Failed to add credential', 'error');
        }
    });
}

function openEditCredentialModal(id) {
    const cred = allCredentials.find(c => c.id == id);
    if (!cred) return;
    document.getElementById('editCredId').value = cred.id;
    document.getElementById('editCredLabel').value = cred.label;
    document.getElementById('editCredUsername').value = cred.username || '';
    document.getElementById('editCredPassword').value = cred.password || '';
    document.getElementById('editCredEnablePassword').value = cred.enable_password || '';
    document.getElementById('editCredDescription').value = cred.description || '';
    document.getElementById('editCredentialModal').classList.add('show');
}

function closeEditCredentialModal() {
    document.getElementById('editCredentialModal').classList.remove('show');
}

function handleUpdateCredential(e) {
    e.preventDefault();
    const cred_id = document.getElementById('editCredId').value;
    const cred = {
        label: document.getElementById('editCredLabel').value,
        username: document.getElementById('editCredUsername').value,
        password: document.getElementById('editCredPassword').value,
        enable_password: document.getElementById('editCredEnablePassword').value,
        description: document.getElementById('editCredDescription').value
    };
    fetch(`/api/credentials/${cred_id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(cred)
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Credential updated successfully');
            closeEditCredentialModal();
            loadCredentials();
        } else {
            showAlert(data.error || 'Failed to update credential', 'error');
        }
    });
}

function deleteCredential(id) {
    if (confirm(t('confirm_delete'))) {
        fetch(`/api/credentials/${id}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert('Credential deleted successfully');
                loadCredentials();
            } else {
                showAlert(data.error || 'Failed to delete credential', 'error');
            }
        });
    }
}

function loadCredentialsToSelect(selectId) {
    fetch('/api/credentials').then(r => r.json()).then(creds => {
        const select = document.getElementById(selectId);
        if (!select) return;
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select credential</option>';
        creds.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = `${c.label} (${c.username})`;
            select.appendChild(opt);
        });
        if (currentValue) select.value = currentValue;
    });
}

function loadGroupsToSelect(selectId) {
    fetch('/api/groups').then(r => r.json()).then(data => {
        const select = document.getElementById(selectId);
        if (!select) return;
        const currentValue = select.value;
        select.innerHTML = '<option value="">No Group</option>';
        data.groups.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.id;
            opt.textContent = g.name;
            select.appendChild(opt);
        });
        if (currentValue) select.value = currentValue;
    });
}

function loadModelsToSelect(selectId) {
    fetch('/api/models').then(r => r.json()).then(models => {
        const select = document.getElementById(selectId);
        if (!select) return;
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select device model</option>';
        models.filter(m => m.enabled).forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.id} - ${m.name}`;
            select.appendChild(opt);
        });
        if (currentValue) select.value = currentValue;
    });
}

// ============ Oxidized Info ============
function refreshOxidizedInfo() {
    fetch('/api/oxidized/info').then(r => r.json()).then(data => {
        document.getElementById('backup-interval-display').textContent = data.interval_display;
    }).catch(err => {
        console.error('Failed to fetch Oxidized info:', err);
        document.getElementById('backup-interval-display').textContent = '1 hour';
    });
}

// ============ Config Manager ============
function switchConfigTab(tabName) {
    document.querySelectorAll('.config-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.config-tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('cfg-tab-' + tabName).classList.add('active');
    document.getElementById('cfg-' + tabName).classList.add('active');
    if (tabName === 'groups') {
        loadGroups();
    } else if (tabName !== 'versions') {
        loadConfig();
    }
}

function loadConfig() {
    fetch('/api/config').then(r => r.json()).then(data => {
        // Basic settings
        document.getElementById('cfg-username').value = data.menu_settings.username || '';
        document.getElementById('cfg-password').value = data.menu_settings.password || '';
        document.getElementById('cfg-interval').value = data.menu_settings.interval || 7200;
        document.getElementById('cfg-threads').value = data.menu_settings.threads || 30;
        document.getElementById('cfg-timeout').value = data.menu_settings.timeout || 300;

        const basicStatus = document.getElementById('basic-status-content');
        if (basicStatus) {
            basicStatus.innerHTML = `
                <div><strong>Username:</strong> ${data.menu_settings.username || '<span style="color:#999;">not set</span>'}</div>
                <div><strong>Interval:</strong> ${data.menu_settings.interval || 7200}s | <strong>Threads:</strong> ${data.menu_settings.threads || 30} | <strong>Timeout:</strong> ${data.menu_settings.timeout || 300}s</div>
                <div><strong>Input:</strong> ${data.menu_settings.input_default || 'ssh'}</div>
            `;
        }

        // SSH settings
        const sshKex = (data.menu_settings.ssh_kex || '').split(',').filter(v => v.trim());
        const sshEnc = (data.menu_settings.ssh_encryption || '').split(',').filter(v => v.trim());
        const sshHmac = (data.menu_settings.ssh_hmac || '').split(',').filter(v => v.trim());
        document.querySelectorAll('input[name="ssh_kex"]').forEach(cb => cb.checked = sshKex.includes(cb.value));
        document.querySelectorAll('input[name="ssh_encryption"]').forEach(cb => cb.checked = sshEnc.includes(cb.value));
        document.querySelectorAll('input[name="ssh_hmac"]').forEach(cb => cb.checked = sshHmac.includes(cb.value));
        document.getElementById('cfg-ssh-secure').checked = data.menu_settings.ssh_secure || false;

        const statusDiv = document.getElementById('ssh-status-content');
        if (statusDiv) {
            if (sshKex.length === 0 && sshEnc.length === 0 && sshHmac.length === 0) {
                statusDiv.innerHTML = '<span style="color:#999;">No SSH algorithms configured</span>';
            } else {
                statusDiv.innerHTML = `
                    <div><strong>KEX:</strong> ${sshKex.length > 0 ? sshKex.join(', ') : '<span style="color:#999;">none</span>'}</div>
                    <div><strong>Encryption:</strong> ${sshEnc.length > 0 ? sshEnc.join(', ') : '<span style="color:#999;">none</span>'}</div>
                    <div><strong>HMAC:</strong> ${sshHmac.length > 0 ? sshHmac.join(', ') : '<span style="color:#999;">none</span>'}</div>
                `;
            }
        }

        // Output settings
        document.getElementById('cfg-output-default').value = data.menu_settings.output_default || 'git';
        document.getElementById('cfg-git-user').value = data.menu_settings.git_user || 'Oxidized';
        document.getElementById('cfg-git-email').value = data.menu_settings.git_email || 'oxidized@example.com';

        const outputStatus = document.getElementById('output-status-content');
        if (outputStatus) {
            outputStatus.innerHTML = `
                <div><strong>Output:</strong> ${data.menu_settings.output_default || 'git'} | <strong>Git User:</strong> ${data.menu_settings.git_user || 'Oxidized'}</div>
                <div><strong>Git Email:</strong> ${data.menu_settings.git_email || 'oxidized@example.com'}</div>
            `;
        }

        // Vars settings
        document.getElementById('cfg-vars-remove-secret').checked = data.menu_settings.vars_remove_secret || false;
        document.getElementById('cfg-vars-ssh-no-keepalive').checked = data.menu_settings.vars_ssh_no_keepalive || false;
        document.getElementById('cfg-vars-ssh-no-exec').checked = data.menu_settings.vars_ssh_no_exec || false;
        document.getElementById('cfg-vars-metadata').checked = data.menu_settings.vars_metadata || false;
        document.getElementById('cfg-vars-enable').value = data.menu_settings.vars_enable || '';

        const varsStatus = document.getElementById('vars-status-content');
        if (varsStatus) {
            const varsList = [];
            if (data.menu_settings.vars_remove_secret) varsList.push('remove_secret');
            if (data.menu_settings.vars_ssh_no_keepalive) varsList.push('ssh_no_keepalive');
            if (data.menu_settings.vars_ssh_no_exec) varsList.push('ssh_no_exec');
            if (data.menu_settings.vars_metadata) varsList.push('metadata');
            const sshKexVar = data.menu_settings.vars_ssh_kex;
            const sshEncVar = data.menu_settings.vars_ssh_encryption;
            varsStatus.innerHTML = `
                <div><strong>Enabled flags:</strong> ${varsList.length > 0 ? varsList.join(', ') : '<span style="color:#999;">none</span>'}</div>
                <div><strong>Vars SSH KEX:</strong> ${sshKexVar || '<span style="color:#999;">default</span>'} | <strong>Encryption:</strong> ${sshEncVar || '<span style="color:#999;">default</span>'}</div>
            `;
        }

        // YAML editor
        document.getElementById('cfg-yaml-editor').value = data.yaml_content || '';
    }).catch(err => {
        console.error('Failed to load config:', err);
        showAlert('Failed to load config: ' + err, 'error');
    });
}

function saveConfigBasic(e) {
    e.preventDefault();
    const settings = {
        username: document.getElementById('cfg-username').value,
        password: document.getElementById('cfg-password').value,
        interval: parseInt(document.getElementById('cfg-interval').value) || 7200,
        threads: parseInt(document.getElementById('cfg-threads').value) || 30,
        timeout: parseInt(document.getElementById('cfg-timeout').value) || 300,
    };
    fetch('/api/config/menu', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({settings: settings, commit_message: 'Update basic settings'})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Basic settings saved!', 'success');
        } else {
            showAlert('Failed to save: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function toggleAll(name, checked) {
    document.querySelectorAll('input[name="' + name + '"]').forEach(cb => cb.checked = checked);
}

function saveConfigSSH(e) {
    e.preventDefault();
    const sshKex = Array.from(document.querySelectorAll('input[name="ssh_kex"]:checked')).map(cb => cb.value).join(',');
    const sshEnc = Array.from(document.querySelectorAll('input[name="ssh_encryption"]:checked')).map(cb => cb.value).join(',');
    const sshHmac = Array.from(document.querySelectorAll('input[name="ssh_hmac"]:checked')).map(cb => cb.value).join(',');
    const settings = {
        ssh_kex: sshKex,
        ssh_encryption: sshEnc,
        ssh_hmac: sshHmac,
        ssh_secure: document.getElementById('cfg-ssh-secure').checked,
    };
    fetch('/api/config/menu', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({settings: settings, commit_message: 'Update SSH settings'})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('SSH settings saved!', 'success');
        } else {
            showAlert('Failed to save: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function saveConfigOutput(e) {
    e.preventDefault();
    const settings = {
        output_default: document.getElementById('cfg-output-default').value,
        git_user: document.getElementById('cfg-git-user').value,
        git_email: document.getElementById('cfg-git-email').value,
    };
    fetch('/api/config/menu', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({settings: settings, commit_message: 'Update output settings'})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Output settings saved!', 'success');
        } else {
            showAlert('Failed to save: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function saveConfigVars(e) {
    e.preventDefault();
    const settings = {
        vars_remove_secret: document.getElementById('cfg-vars-remove-secret').checked,
        vars_ssh_no_keepalive: document.getElementById('cfg-vars-ssh-no-keepalive').checked,
        vars_ssh_no_exec: document.getElementById('cfg-vars-ssh-no-exec').checked,
        vars_metadata: document.getElementById('cfg-vars-metadata').checked,
        vars_enable: document.getElementById('cfg-vars-enable').value,
    };
    fetch('/api/config/menu', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({settings: settings, commit_message: 'Update vars settings'})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Vars settings saved!', 'success');
        } else {
            showAlert('Failed to save: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function formatYaml() {
    try {
        const editor = document.getElementById('cfg-yaml-editor');
        const yaml = jsyaml.load(editor.value);
        editor.value = jsyaml.dump(yaml, {indent: 2, lineWidth: -1});
    } catch(e) {
        showAlert('YAML format error: ' + e.message, 'error');
    }
}

function validateYamlConfig() {
    const yaml = document.getElementById('cfg-yaml-editor').value;
    fetch('/api/config/validate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({yaml_content: yaml})
    }).then(r => r.json()).then(data => {
        const status = document.getElementById('yaml-validate-status');
        if (data.valid) {
            status.textContent = '✅ Valid YAML';
            status.style.color = 'green';
        } else {
            status.textContent = '❌ Invalid: ' + (data.errors || []).join(', ');
            status.style.color = 'red';
        }
    });
}

function saveYamlConfig() {
    const yaml = document.getElementById('cfg-yaml-editor').value;
    const commit = document.getElementById('cfg-yaml-commit').value || 'Update YAML config';
    fetch('/api/config/yaml', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({yaml_content: yaml, commit_message: commit})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('YAML config saved!', 'success');
            loadConfigVersions();
        } else {
            showAlert('Failed to save: ' + (data.errors || data.error || 'Unknown error'), 'error');
        }
    });
}

function loadConfigVersions() {
    fetch('/api/config/versions').then(r => r.json()).then(data => {
        const tbody = document.getElementById('config-versions-list');
        const diffFrom = document.getElementById('diff-from');
        const diffTo = document.getElementById('diff-to');

        if (data.versions && data.versions.length > 0) {
            const versionOptions = data.versions.map(v =>
                `<option value="${v.version}">v${v.version} - ${v.commit_message || 'No message'} (${v.created_at})</option>`
            ).join('');

            tbody.innerHTML = data.versions.map(v => `
                <tr>
                    <td>v${v.version}</td>
                    <td>${v.created_at}</td>
                    <td>${v.commit_message || ''}</td>
                    <td>
                        <button class="btn btn-sm" onclick="rollbackConfig(${v.version})">↩️ Rollback</button>
                    </td>
                </tr>
            `).join('');

            if (diffFrom) diffFrom.innerHTML = versionOptions;
            if (diffTo) diffTo.innerHTML = versionOptions;

            if (diffFrom && diffTo && data.versions.length >= 2) {
                diffFrom.value = data.versions[0].version;
                diffTo.value = data.versions[1].version;
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No versions found</td></tr>';
        }
    });
}

function rollbackConfig(version) {
    if (!confirm('Rollback to version ' + version + '?')) return;
    fetch('/api/config/rollback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({version: version, commit_message: 'Rollback to v' + version})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Rolled back to v' + version + '!', 'success');
            loadConfig();
            loadConfigVersions();
        } else {
            showAlert('Failed to rollback: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function applyConfig() {
    fetch('/api/config/apply', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({restart: true})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Config applied and Oxidized restarted!', 'success');
        } else {
            showAlert('Failed: ' + (data.error || 'Unknown error'), 'error');
        }
    });
}

function showSelectedDiff() {
    const fromVersion = document.getElementById('diff-from').value;
    const toVersion = document.getElementById('diff-to').value;

    if (!fromVersion || !toVersion) {
        showAlert('Please select both versions to compare', 'error');
        return;
    }

    const diffContent = document.getElementById('config-diff-content');
    diffContent.innerHTML = '<div style="text-align: center; padding: 20px;">Loading diff...</div>';
    document.getElementById('config-diff-container').style.display = 'block';

    fetch(`/api/config/diff?from=${fromVersion}&to=${toVersion}`).then(r => r.json()).then(data => {
        if (data.error) {
            diffContent.innerHTML = `<div style="color: red; padding: 20px;">Error: ${data.error}</div>`;
            return;
        }

        const fromLines = data.diff.filter(d => d.type !== 'insert');
        const toLines = data.diff.filter(d => d.type !== 'delete');

        let html = `<div style="display: flex; font-family: monospace; font-size: 12px; border: 1px solid #ddd;">
            <div style="flex: 1; border-right: 1px solid #ddd; overflow-x: auto;">
                <div style="background: #f5f5f5; padding: 5px; font-weight: bold; position: sticky; top: 0;">
                    Version ${data.from.version} (${data.from.commit_message || 'No message'})
                </div>
                <div style="padding: 5px;">`;
        fromLines.forEach(line => {
            if (line.type === 'delete') {
                html += `<div style="background: #ffe6e6; color: #c00; padding: 2px 5px;">- ${escapeHtml(line.content)}</div>`;
            } else if (line.type === 'equal') {
                html += `<div style="padding: 2px 5px; color: #666;">  ${escapeHtml(line.content)}</div>`;
            }
        });
        html += `</div></div>`;

        html += `<div style="flex: 1; overflow-x: auto;">
                <div style="background: #f5f5f5; padding: 5px; font-weight: bold; position: sticky; top: 0;">
                    Version ${data.to.version} (${data.to.commit_message || 'No message'})
                </div>
                <div style="padding: 5px;">`;
        toLines.forEach(line => {
            if (line.type === 'insert') {
                html += `<div style="background: #e6ffe6; color: #080; padding: 2px 5px;">+ ${escapeHtml(line.content)}</div>`;
            } else if (line.type === 'equal') {
                html += `<div style="padding: 2px 5px; color: #666;">  ${escapeHtml(line.content)}</div>`;
            }
        });
        html += `</div></div></div>`;

        const added = data.diff.filter(d => d.type === 'insert').length;
        const removed = data.diff.filter(d => d.type === 'delete').length;
        html = `<div style="margin-bottom: 10px; font-size: 12px; color: #666;">
            <span style="color: #080;">+${added} added</span> |
            <span style="color: #c00;">-${removed} removed</span>
        </div>` + html;

        diffContent.innerHTML = html;
    }).catch(err => {
        diffContent.innerHTML = `<div style="color: red; padding: 20px;">Failed to load diff: ${err.message}</div>`;
    });
}

// ============ Role-Based Visibility ============
function applyRoleBasedVisibility() {
    const isAdmin = window.currentUserRole === 'admin';

    const usersTab = document.getElementById('tab-users');
    if (usersTab) usersTab.style.display = isAdmin ? '' : 'none';

    const configTab = document.getElementById('tab-config');
    if (configTab) configTab.style.display = isAdmin ? '' : 'none';

    const credTab = document.getElementById('tab-credentials');
    if (credTab) credTab.style.display = isAdmin ? '' : 'none';

    const addGroupBtns = document.querySelectorAll('[onclick="openAddGroupModal()"]');
    addGroupBtns.forEach(btn => {
        btn.style.display = isAdmin ? '' : 'none';
    });

    const groupActionBtns = document.querySelectorAll('[onclick^="openEditGroupModal"]');
    groupActionBtns.forEach(btn => {
        btn.style.display = isAdmin ? '' : 'none';
    });

    const groupDeleteBtns = document.querySelectorAll('[onclick^="deleteGroup"]');
    groupDeleteBtns.forEach(btn => {
        btn.style.display = isAdmin ? '' : 'none';
    });

    const modelSaveBtn = document.querySelector('button[onclick="saveModels()"]');
    if (modelSaveBtn) modelSaveBtn.style.display = isAdmin ? '' : 'none';

    const addCredBtn = document.querySelector('button[onclick="openAddCredentialModal()"]');
    if (addCredBtn) addCredBtn.style.display = isAdmin ? '' : 'none';

    const deleteUserBtns = document.querySelectorAll('[onclick^="deleteUser"]');
    deleteUserBtns.forEach(btn => {
        btn.style.display = isAdmin ? '' : 'none';
    });
}

// ============ Initialization ============
let configLoaded = false;
const _originalSwitchTab = switchTab;
switchTab = function(tab) {
    _originalSwitchTab(tab);
    if (tab === 'config' && !configLoaded) {
        loadConfig();
        loadConfigVersions();
        configLoaded = true;
    }
};

fetch('/api/user-info').then(r => r.json()).then(data => {
    document.getElementById('usernameBtn').textContent = data.username;
    window.currentUserRole = data.role || 'user';
    applyRoleBasedVisibility();
});

// Close any open modal when Escape is pressed
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            modal.classList.remove('show');
        });
    }
});

updateUI();
refreshOxidizedInfo();
refreshOxidizedStatus();
setInterval(refreshOxidizedStatus, 60000);
