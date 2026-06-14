const API = 'http://localhost:8000/api/v1';

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body instanceof FormData) opts.body = body;
  else if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  const r = await fetch(API + path, opts);
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.detail || r.statusText); }
  return r.json();
}

const get = (p) => api('GET', p);
const post = (p, b) => api('POST', p, b);
const del = (p) => api('DELETE', p);

// JD
const getJDs = () => get('/jd/');
const createJD = (d) => post('/jd/', d);
const deleteJD = (id) => del(`/jd/${id}`);

// Candidates — only append jd_id param if actually set
const getCandidates = (jdId) => get('/candidates/' + (jdId ? `?jd_id=${jdId}` : ''));
const getCandidate = (id) => get(`/candidates/${id}`);
const deleteCandidate = (id) => del(`/candidates/${id}`);
const uploadResumes = (files, jdId) => {
  const fd = new FormData();
  files.forEach(f => fd.append('files', f));
  const qs = jdId ? `?job_description_id=${jdId}` : '';
  return api('POST', `/candidates/upload${qs}`, fd);
};

const matchCandidates = (ids, jdId) => post('/match', { candidate_ids: ids, job_description_id: jdId });
const getAnalytics = (jdId) => get('/analytics' + (jdId ? `?jd_id=${jdId}` : ''));

// Toast
function toast(msg, type = 'info') {
  let c = document.getElementById('toasts');
  if (!c) { c = document.createElement('div'); c.id = 'toasts'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${type==='ok'?'✓':type==='err'?'✕':'ℹ'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function scoreColor(s) {
  if (s == null) return '#444460';
  if (s >= 80) return '#10b981';
  if (s >= 60) return '#6366f1';
  if (s >= 40) return '#f59e0b';
  return '#f43f5e';
}

const skillTag = s => `<span class="tag tag-skill">${s}</span>`;
const matchTag = s => `<span class="tag tag-match">${s}</span>`;
const missTag  = s => `<span class="tag tag-miss">${s}</span>`;
const prefTag  = s => `<span class="tag tag-pref">${s}</span>`;

function progBar(val, max, color) {
  const pct = Math.min(100, (val / (max || 1)) * 100);
  const c = color || scoreColor(pct);
  return `<div class="prog"><div class="prog-bar" style="width:${pct}%;background:${c}"></div></div>`;
}

function emptyState(icon, title, desc, action = '') {
  return `<div class="empty"><div class="empty-ic">${icon}</div><h3>${title}</h3><p>${desc}</p>${action}</div>`;
}

// Load JD dropdown — always starts with "All candidates" option
async function loadJDSelect(sel, onChange) {
  const jds = await getJDs().catch(() => []);
  sel.innerHTML = '<option value="">All candidates</option>' +
    jds.map(j => `<option value="${j.id}">${j.title}${j.company ? ' — ' + j.company : ''}</option>`).join('');
  if (onChange) sel.addEventListener('change', () => onChange(sel.value ? +sel.value : null));
  return jds;
}

function setLoading(btn, yes) {
  if (yes) { btn._txt = btn.innerHTML; btn.innerHTML = '<span class="spin"></span> Working…'; btn.disabled = true; }
  else { btn.innerHTML = btn._txt; btn.disabled = false; }
}

const ICONS = {
  upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`,
  file:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
  users:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
  bar:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
  zap:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
  trash:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>`,
  eye:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
  check:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="20 6 9 17 4 12"/></svg>`,
  x:      `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
  down:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  spark:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`,
  trend:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  alert:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
};

function sidebarHTML(active) {
  const links = [
    ['index.html','dashboard','Dashboard',ICONS.bar],
    ['upload.html','upload','Upload Resumes',ICONS.upload],
    ['jd.html','jd','Job Description',ICONS.file],
    ['candidates.html','candidates','Candidates',ICONS.users],
    ['ranking.html','ranking','Rankings',ICONS.zap],
    ['analytics.html','analytics','Analytics',ICONS.bar],
    ['reports.html','reports','Reports',ICONS.down],
  ];
  return `<aside class="sidebar">
    <a href="index.html" class="logo">
      <div class="logo-icon">🧠</div>
      <div><strong>ResumeIQ</strong><small>AI Recruitment</small></div>
    </a>
    <nav>
      ${links.map(([href,page,label,icon]) =>
        `<a href="${href}" class="nav-link${active===page?' active':''}">${icon}<span>${label}</span></a>`
      ).join('')}
    </nav>
    <div class="sidebar-foot">
      <div style="display:flex;align-items:center;gap:8px;padding:8px;background:var(--surface);border-radius:var(--r-sm);border:1px solid var(--border)">
        <div style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,var(--brand),#c084fc);flex-shrink:0"></div>
        <div><div style="font-size:12px;font-weight:600;color:var(--text)">Recruiter</div><div style="font-size:10px;color:var(--text3)">Pro Plan</div></div>
      </div>
    </div>
  </aside>`;
}
