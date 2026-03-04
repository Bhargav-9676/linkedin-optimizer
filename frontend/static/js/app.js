/* ============================================================
   LinkedIn Profile Optimizer — Frontend JavaScript
   All API calls go to Flask backend which reads Groq key
   from config.env via config.py
   ============================================================ */

const API = '';   // same-origin Flask server
let currentAuditId = null;
let currentAuditData = null;

// ── INIT ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkAIStatus();
  setupUrlInput();
});

// ── AI STATUS CHECK ───────────────────────────────────────────────────────
async function checkAIStatus() {
  try {
    const res = await fetch(`${API}/api/status`);
    const d   = await res.json();
    const dot  = document.getElementById('ai-dot');
    const lbl  = document.getElementById('ai-label');
    if (d.ai.groq_ready) {
      dot.className = 'ai-dot ready';
      lbl.textContent = `Groq · ${d.ai.model}`;
    } else if (d.ai.claude_ready) {
      dot.className = 'ai-dot ready';
      lbl.textContent = 'Claude API';
    } else {
      dot.className = 'ai-dot warn';
      lbl.textContent = 'Template mode — add Groq key';
    }
  } catch {
    document.getElementById('ai-dot').className = 'ai-dot error';
    document.getElementById('ai-label').textContent = 'Server offline';
  }
}

// ── URL INPUT VALIDATION ──────────────────────────────────────────────────
function setupUrlInput() {
  const input = document.getElementById('f-url');
  const okEl  = document.getElementById('url-ok');
  const hint  = document.getElementById('url-hint');
  const wrap  = input.closest('.url-wrap');

  input.addEventListener('input', () => {
    const val = input.value.trim();
    if (!val) {
      wrap.classList.remove('valid', 'invalid');
      okEl.classList.add('hidden');
      hint.className = 'url-hint';
      hint.textContent = 'Enter a valid LinkedIn profile URL';
      return;
    }
    if (isValidLinkedInUrl(val)) {
      wrap.classList.add('valid');
      wrap.classList.remove('invalid');
      okEl.classList.remove('hidden');
      hint.className = 'url-hint';
      hint.textContent = '✓ Valid LinkedIn URL';
    } else if (val.length > 6) {
      wrap.classList.add('invalid');
      wrap.classList.remove('valid');
      okEl.classList.add('hidden');
      hint.className = 'url-hint error';
      hint.textContent = 'Must be a linkedin.com/in/ or linkedin.com/company/ URL';
    }
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') runAnalysis();
  });
}

function isValidLinkedInUrl(url) {
  return /linkedin\.com\/(in|company|pub)\//.test(url) ||
         /^[\w-]{3,}$/.test(url.trim()); // just a handle
}

function normalizeUrl(val) {
  val = val.trim();
  if (!val) return '';
  if (val.startsWith('http')) return val;
  if (val.includes('linkedin.com')) return 'https://' + val;
  return `https://www.linkedin.com/in/${val}`;
}

// ── RUN ANALYSIS ──────────────────────────────────────────────────────────
async function runAnalysis() {
  const rawUrl = document.getElementById('f-url').value.trim();
  if (!rawUrl) {
    showToast('Please enter a LinkedIn profile URL', 'error');
    document.getElementById('f-url').focus();
    return;
  }

  const url = normalizeUrl(rawUrl);

  const payload = {
    linkedin_url:       url,
    client_name:        document.getElementById('f-name').value.trim(),
    client_type:        document.getElementById('f-type').value,
    objective:          document.getElementById('f-obj').value,
    industry:           document.getElementById('f-industry').value.trim(),
    target_audience:    document.getElementById('f-audience').value.trim(),
    additional_context: document.getElementById('f-ctx').value.trim(),
  };

  // Switch to loading view
  showSection('loading');
  startLoadingSteps();

  const btn = document.getElementById('go-btn');
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/api/audit`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || 'Analysis failed');
    }

    currentAuditId   = data.audit_id;
    currentAuditData = data;
    renderResults(data);
    showSection('results');
    showToast('✅ Profile analyzed successfully!', 'success');

  } catch (err) {
    showSection('form');
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

// ── LOADING STEP ANIMATION ────────────────────────────────────────────────
function startLoadingSteps() {
  const steps = ['ls1','ls2','ls3','ls4'];
  const msgs  = [
    'Scanning all 6 profile sections…',
    'Scoring each element with AI…',
    'Generating specific recommendations…',
    'Building your full report…',
  ];
  let i = 0;
  steps.forEach(id => {
    const el = document.getElementById(id);
    el.className = 'lstep';
  });
  document.getElementById('load-title').textContent = 'Analyzing with Groq AI…';

  const tick = () => {
    if (i > 0) {
      document.getElementById(steps[i-1]).className = 'lstep done';
    }
    if (i < steps.length) {
      document.getElementById(steps[i]).className = 'lstep act';
      document.getElementById('load-title').textContent = msgs[i];
      i++;
      setTimeout(tick, 900 + Math.random() * 400);
    }
  };
  setTimeout(tick, 300);
}

// ── SHOW/HIDE SECTIONS ─────────────────────────────────────────────────────
function showSection(name) {
  document.getElementById('hero').classList.toggle('hidden', name !== 'form');
  document.getElementById('form-section').classList.toggle('hidden', name !== 'form');
  document.getElementById('loading-section').classList.toggle('hidden', name !== 'loading');
  document.getElementById('results').classList.toggle('hidden', name !== 'results');
  if (name !== 'loading') {
    document.querySelectorAll('.lstep').forEach(el => el.className = 'lstep');
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetForm() {
  showSection('form');
  currentAuditId   = null;
  currentAuditData = null;
}

// ── RENDER RESULTS ────────────────────────────────────────────────────────
function renderResults(data) {
  const audit    = data.audit;
  const sections = audit.sections || {};

  // Top bar
  document.getElementById('res-url').textContent  = data.linkedin_url || '';
  document.getElementById('res-meta').textContent =
    `${data.audit.profile_strength || ''} · Analyzed ${formatTime(data.analyzed_at)} · Audit #${data.audit_id}`;

  const provMap = { groq: '⚡ Groq · Free', claude: '🤖 Claude', template: '📋 Template' };
  document.getElementById('prov-badge').textContent = provMap[data.ai_provider] || data.ai_provider;

  // Animate score ring
  const score      = audit.overall_score || 0;
  const circumference = 326.73;
  const offset     = circumference - (score / 100) * circumference;
  const scoreEl    = document.getElementById('score-progress');
  setTimeout(() => {
    scoreEl.style.strokeDashoffset = offset;
    scoreEl.style.stroke = scoreColor(score);
  }, 200);

  animateNumber('score-number', score, 1200);

  // Strength badge
  const strength = (audit.profile_strength || 'Intermediate').toLowerCase();
  const strengthEl = document.getElementById('strength-tag');
  strengthEl.textContent = audit.profile_strength || 'Intermediate';
  strengthEl.className = `strength-tag tag-${strength.replace(' ', '')}`;

  // Summary
  document.getElementById('score-summary').textContent = audit.summary || '';

  // Section bars
  renderSectionBars(sections);

  // Top priorities
  renderPriorities(audit.top_priorities || []);

  // Quick wins
  const qwHd   = document.getElementById('qw-hd');
  const qwList = document.getElementById('qw-list');
  if (audit.quick_wins && audit.quick_wins.length) {
    qwHd.style.display = 'flex';
    qwList.innerHTML = audit.quick_wins.map(w => `
      <div class="qw-item">
        <span class="qw-icon">⚡</span>
        <span class="qw-text">${esc(w)}</span>
      </div>`).join('');
  } else {
    qwHd.style.display = 'none';
    qwList.innerHTML = '';
  }

  // Section cards
  renderSectionCards(sections, data.audit_id,
    document.getElementById('f-obj').value,
    document.getElementById('f-industry').value,
    document.getElementById('f-audience').value
  );
}

// ── SECTION BARS ──────────────────────────────────────────────────────────
const SECTION_META = {
  profile_picture:  { label: 'Profile Picture', icon: '📷' },
  headline:         { label: 'Headline',         icon: '✍️'  },
  background_image: { label: 'Background',       icon: '🖼️'  },
  about:            { label: 'About',             icon: '📝'  },
  featured:         { label: 'Featured',          icon: '⭐'  },
  experience:       { label: 'Experience',        icon: '💼'  },
};

function renderSectionBars(sections) {
  const grid = document.getElementById('bars-grid');
  grid.innerHTML = Object.entries(sections).map(([key, sec]) => {
    const meta  = SECTION_META[key] || { label: key, icon: '•' };
    const score = sec.score || 0;
    const tier  = scoreTier(score);
    return `
    <div class="bar-item" onclick="openSectionModal('${key}')">
      <div class="bar-top">
        <div class="bar-name">${meta.icon} ${meta.label}</div>
        <div class="bar-score" style="color:${scoreColor(score)}">${score}</div>
      </div>
      <div class="bar-track">
        <div class="bar-fill ${tier}" style="width:0%" id="barfill-${key}"></div>
      </div>
      <div class="bar-status status-${sec.status || 'needs_work'}">${formatStatus(sec.status)}</div>
    </div>`;
  }).join('');

  // Animate fills after paint
  setTimeout(() => {
    Object.entries(sections).forEach(([key, sec]) => {
      const el = document.getElementById(`barfill-${key}`);
      if (el) el.style.width = `${sec.score || 0}%`;
    });
  }, 300);
}

// ── PRIORITIES ────────────────────────────────────────────────────────────
function renderPriorities(priorities) {
  const list = document.getElementById('priorities-list');
  list.innerHTML = priorities.map((p, i) => `
    <div class="priority-item">
      <div class="priority-num">${i + 1}</div>
      <div class="priority-text">${esc(p)}</div>
    </div>`).join('');
}

// ── SECTION CARDS ─────────────────────────────────────────────────────────
function renderSectionCards(sections, auditId, objective, industry, audience) {
  const grid = document.getElementById('cards-grid');
  grid.innerHTML = Object.entries(sections).map(([key, sec]) => {
    const meta   = SECTION_META[key] || { label: key, icon: '•' };
    const score  = sec.score || 0;
    const tier   = scoreTier(score);
    const issues = (sec.issues || []).slice(0, 2);
    return `
    <div class="section-card ${tier}" onclick="openSectionModal('${key}')">
      <div class="sc-top">
        <div class="sc-name"><span class="sc-icon">${meta.icon}</span>${meta.label}</div>
        <div class="sc-score ${tier}">${score}</div>
      </div>
      <div class="sc-bar-track">
        <div class="sc-bar-fill ${tier}" style="width:${score}%;background:${scoreColor(score)}"></div>
      </div>
      <ul class="sc-issues">
        ${issues.map(iss => `<li class="sc-issue">${esc(iss)}</li>`).join('')}
      </ul>
      <div class="sc-cta">View details & AI rewrite →</div>
    </div>`;
  }).join('');
}

// ── SECTION MODAL ─────────────────────────────────────────────────────────
function openSectionModal(sectionKey) {
  if (!currentAuditData) return;
  const audit   = currentAuditData.audit;
  const sections = audit.sections || {};
  const sec     = sections[sectionKey];
  if (!sec) return;

  const meta  = SECTION_META[sectionKey] || { label: sectionKey, icon: '•' };
  const score = sec.score || 0;
  const tier  = scoreTier(score);

  const canRewrite = ['headline', 'about', 'experience'].includes(sectionKey);

  const modalBody = `
    <div class="modal-section-header">
      <div class="modal-section-title">
        <span>${meta.icon}</span>
        <span>${meta.label}</span>
      </div>
      <div class="modal-score-row">
        <div class="modal-score-num" style="color:${scoreColor(score)}">${score}</div>
        <div>
          <div style="font-size:12px;color:var(--text3)">out of 100</div>
          <div class="bar-status status-${sec.status || 'needs_work'}" style="font-size:11px">${formatStatus(sec.status)}</div>
        </div>
        <div class="sc-bar-track" style="flex:1;margin-left:16px;margin-top:0">
          <div class="sc-bar-fill" style="width:${score}%;background:${scoreColor(score)}"></div>
        </div>
      </div>
    </div>

    <div class="modal-body">

      ${sec.issues && sec.issues.length ? `
      <div class="modal-block">
        <div class="modal-block-title">❌ Issues Found</div>
        <ul class="issues-list">
          ${sec.issues.map(iss => `
            <li class="issue-item">
              <span class="issue-icon">✕</span>
              <span>${esc(iss)}</span>
            </li>`).join('')}
        </ul>
      </div>` : ''}

      ${sec.suggestions && sec.suggestions.length ? `
      <div class="modal-block">
        <div class="modal-block-title">✅ Recommendations</div>
        <ul class="suggestions-list">
          ${sec.suggestions.map(s => `
            <li class="suggestion-item">
              <span class="sugg-icon">→</span>
              <span>${esc(s)}</span>
            </li>`).join('')}
        </ul>
      </div>` : ''}

      ${sec.example ? `
      <div class="modal-block">
        <div class="modal-block-title">💡 What Good Looks Like</div>
        <div class="example-box">
          <strong>Example</strong>
          ${esc(sec.example)}
        </div>
      </div>` : ''}

      ${canRewrite ? `
      <div class="modal-block">
        <div class="rewrite-section">
          <div class="rewrite-title">
            ✨ AI Rewrite with Groq
            <span style="font-size:11px;color:var(--text3);font-weight:400;margin-left:4px">— paste current content for a personalized rewrite</span>
          </div>
          <textarea class="rewrite-input" id="rw-input-${sectionKey}"
            placeholder="Paste current ${meta.label.toLowerCase()} content here (leave blank for a fresh version)…"></textarea>
          <button class="rewrite-btn" id="rw-btn-${sectionKey}"
            onclick="doRewrite('${sectionKey}')">
            ✨ Rewrite with AI
          </button>
          <div id="rw-result-${sectionKey}"></div>
        </div>
      </div>` : ''}

    </div>`;

  document.getElementById('modal-body').innerHTML = modalBody;
  document.getElementById('modal-bg').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal-bg').classList.add('hidden');
  document.body.style.overflow = '';
}

// ── AI REWRITE ────────────────────────────────────────────────────────────
async function doRewrite(sectionKey) {
  if (!currentAuditId) return;

  const inputEl  = document.getElementById(`rw-input-${sectionKey}`);
  const btnEl    = document.getElementById(`rw-btn-${sectionKey}`);
  const resultEl = document.getElementById(`rw-result-${sectionKey}`);

  btnEl.disabled     = true;
  btnEl.textContent  = '⏳ Rewriting with Groq…';
  resultEl.innerHTML = '';

  try {
    const res = await fetch(`${API}/api/audit/${currentAuditId}/rewrite`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        section:          sectionKey,
        current_content:  inputEl.value.trim(),
        industry:         document.getElementById('f-industry').value,
        target_audience:  document.getElementById('f-audience').value,
      }),
    });

    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || 'Rewrite failed');

    renderRewriteResult(sectionKey, data.result, data.ai_provider);
    showToast('✅ Rewrite complete!', 'success');

  } catch (err) {
    resultEl.innerHTML = `<div style="color:var(--red);font-size:13px;margin-top:10px">Error: ${esc(err.message)}</div>`;
    showToast(`Rewrite failed: ${err.message}`, 'error');
  } finally {
    btnEl.disabled    = false;
    btnEl.textContent = '✨ Rewrite with AI';
  }
}

function renderRewriteResult(sectionKey, result, provider) {
  const resultEl = document.getElementById(`rw-result-${sectionKey}`);
  const provTxt  = provider === 'groq' ? '⚡ Groq' : provider === 'claude' ? '🤖 Claude' : '📋 Template';

  // Headline returns variations
  if (sectionKey === 'headline' && result.variations) {
    const best = result.best_pick || 0;
    resultEl.innerHTML = `
      <div style="margin-top:14px">
        <div class="modal-block-title" style="margin-bottom:10px">
          Headline Variations <span style="color:var(--gold);font-size:11px;margin-left:8px">${provTxt}</span>
        </div>
        ${result.variations.map((v, i) => `
          <div class="variation-card ${i === best ? 'best' : ''}">
            <button class="copy-btn" onclick="copyText('${esc(v).replace(/'/g,"\\'")}')">Copy</button>
            ${i === best ? '<span style="font-size:10px;color:var(--gold);font-weight:700;text-transform:uppercase;letter-spacing:0.5px;display:block;margin-bottom:4px">⭐ Best Pick</span>' : ''}
            ${esc(v)}
          </div>`).join('')}
        ${result.reason ? `<div style="font-size:12px;color:var(--text3);margin-top:8px;font-style:italic">${esc(result.reason)}</div>` : ''}
      </div>`;
    return;
  }

  // About / Experience returns rewritten text
  const text = result.rewritten || JSON.stringify(result, null, 2);
  resultEl.innerHTML = `
    <div style="margin-top:14px">
      <div class="modal-block-title" style="margin-bottom:10px">
        Rewritten ${SECTION_META[sectionKey]?.label || sectionKey}
        <span style="color:var(--gold);font-size:11px;margin-left:8px">${provTxt}</span>
        <button class="copy-btn" style="float:right" onclick="copyText(this.getAttribute('data-txt'))"
          data-txt="${esc(text).replace(/"/g,'&quot;')}">Copy</button>
      </div>
      <div class="rewrite-result">${esc(text)}</div>
      ${result.hook ? `<div style="margin-top:10px;font-size:12px;color:var(--text3)"><strong style="color:var(--gold)">Hook (first line):</strong> ${esc(result.hook)}</div>` : ''}
    </div>`;
}

// ── HISTORY ───────────────────────────────────────────────────────────────
async function toggleHistory() {
  const bg    = document.getElementById('hist-bg');
  const panel = document.getElementById('hist-panel');
  const open  = !panel.classList.contains('hidden');

  if (open) {
    bg.classList.add('hidden');
    panel.classList.add('hidden');
  } else {
    bg.classList.remove('hidden');
    panel.classList.remove('hidden');
    await loadHistory();
  }
}

async function loadHistory() {
  const listEl = document.getElementById('hist-list');
  listEl.innerHTML = '<div style="padding:20px;color:var(--text3);font-size:13px">Loading…</div>';

  try {
    const res  = await fetch(`${API}/api/audits`);
    const data = await res.json();

    if (!data.length) {
      listEl.innerHTML = '<div style="padding:20px;color:var(--text3);font-size:13px;text-align:center">No audits yet</div>';
      return;
    }

    listEl.innerHTML = data.map(a => {
      const score = a.overall_score || 0;
      return `
        <div class="hist-item" onclick="loadHistoryAudit(${a.id})">
          <div class="hist-url">${esc(a.linkedin_url || '')}</div>
          <div class="hist-name">${esc(a.client_name || 'Unnamed profile')}</div>
          <div class="hist-bottom">
            <div class="hist-score" style="color:${scoreColor(score)}">${score}</div>
            <div class="hist-date">${formatTime(a.created_at)}</div>
          </div>
        </div>`;
    }).join('');
  } catch {
    listEl.innerHTML = '<div style="padding:20px;color:var(--red);font-size:13px">Failed to load history</div>';
  }
}

async function loadHistoryAudit(auditId) {
  toggleHistory();
  showSection('loading');
  startLoadingSteps();

  try {
    const res  = await fetch(`${API}/api/audit/${auditId}`);
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || 'Not found');

    // Adapt shape to match what renderResults expects
    const auditData = data.audit_data || {};
    currentAuditId   = auditId;
    currentAuditData = {
      audit_id:     auditId,
      linkedin_url: data.linkedin_url,
      audit:        auditData,
      ai_provider:  data.ai_provider,
      analyzed_at:  data.created_at,
    };

    // Pre-fill form fields so rewrites work
    const rawInput = JSON.parse(data.raw_input || '{}');
    document.getElementById('f-obj').value      = rawInput.objective || 'lead_generation';
    document.getElementById('f-industry').value = rawInput.industry  || '';
    document.getElementById('f-audience').value = rawInput.target_audience || '';

    renderResults(currentAuditData);
    showSection('results');
  } catch (err) {
    showSection('form');
    showToast(`Failed to load audit: ${err.message}`, 'error');
  }
}

// ── UTILITIES ─────────────────────────────────────────────────────────────
function esc(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function scoreColor(score) {
  if (score >= 75) return 'var(--green)';
  if (score >= 50) return 'var(--amber)';
  return 'var(--red)';
}

function scoreTier(score) {
  if (score >= 75) return 'high';
  if (score >= 50) return 'mid';
  return 'low';
}

function formatStatus(status) {
  const map = {
    strong:     '✦ Strong',
    average:    '◈ Average',
    needs_work: '✕ Needs Work',
  };
  return map[status] || status || 'Needs Work';
}

function formatTime(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
           ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } catch { return ts; }
}

function animateNumber(elId, target, duration = 1000) {
  const el    = document.getElementById(elId);
  const start = performance.now();
  const step  = (now) => {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(ease * target);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success');
  } catch {
    showToast('Copy failed — please select and copy manually', 'error');
  }
}

function showToast(message, type = 'info') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const wrap  = document.getElementById('toasts');
  const el    = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${esc(message)}</span>`;
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.opacity    = '0';
    el.style.transition = 'opacity 0.4s';
    setTimeout(() => el.remove(), 400);
  }, 3500);
}
