<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LinkedIn Profile Optimizer — AI Audit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/style.css">
</head>
<body>

<!-- HEADER -->
<header class="header">
  <div class="header-inner">
    <div class="logo">
      <svg width="26" height="26" viewBox="0 0 28 28"><rect width="28" height="28" rx="6" fill="#0A66C2"/><path d="M8 10h3v10H8V10zm1.5-4.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM13 10h3v1.4c.4-.8 1.4-1.6 3-1.6 3.2 0 3.8 2 3.8 4.6V20h-3v-5c0-1.2 0-2.8-1.7-2.8S16 13.2 16 15v5h-3V10z" fill="white"/></svg>
      <span>Profile<em>Optimizer</em></span>
    </div>
    <div class="header-right">
      <div class="ai-pill" id="ai-pill">
        <span class="ai-dot" id="ai-dot"></span>
        <span id="ai-label">Checking...</span>
      </div>
      <button class="btn-hist" onclick="toggleHistory()">⏱ History</button>
    </div>
  </div>
</header>

<main>

  <!-- ── HERO ── -->
  <section class="hero" id="hero">
    <div class="hero-left">
      <div class="hero-chip">✦ Free · Groq API · llama3-8b</div>
      <h1>Turn your LinkedIn<br>into a <em>lead machine</em></h1>
      <p>Paste a profile URL and get an AI-powered audit — scores, issues, and specific suggestions for every section in seconds.</p>
      <div class="hero-stats">
        <div class="hstat"><strong>6</strong><span>Sections Scored</span></div>
        <div class="hstat"><strong>AI</strong><span>Suggestions</span></div>
        <div class="hstat"><strong>100%</strong><span>Free</span></div>
      </div>
    </div>
    <div class="hero-right">
      <div class="preview-card">
        <div class="prev-banner"></div>
        <div class="prev-av"></div>
        <div class="prev-meta">
          <div class="prev-line w70 thick"></div>
          <div class="prev-line w50"></div>
          <div class="prev-line w35 blue"></div>
        </div>
        <div class="prev-rows">
          <div class="prev-row"><span>Headline</span><div class="prev-bar" style="--p:55%"><div class="prev-fill low"></div></div><b>55</b></div>
          <div class="prev-row"><span>About</span><div class="prev-bar" style="--p:38%"><div class="prev-fill low"></div></div><b>38</b></div>
          <div class="prev-row"><span>Featured</span><div class="prev-bar" style="--p:20%"><div class="prev-fill low"></div></div><b>20</b></div>
          <div class="prev-row"><span>Experience</span><div class="prev-bar" style="--p:72%"><div class="prev-fill mid"></div></div><b>72</b></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ── FORM ── -->
  <section class="form-wrap" id="form-section">
    <div class="form-card">
      <div class="form-head">
        <h2>Analyze a LinkedIn Profile</h2>
        <p>Paste any URL and tell us the goal</p>
      </div>

      <div class="url-wrap">
        <div class="url-prefix">🔗</div>
        <input type="text" id="f-url" class="url-input"
          placeholder="https://linkedin.com/in/username"
          autocomplete="off" spellcheck="false">
        <div class="url-ok hidden" id="url-ok">✓</div>
      </div>
      <div class="url-hint" id="url-hint">Enter a valid LinkedIn profile URL</div>

      <div class="fgrid">
        <div class="fg">
          <label>Client Name <em>optional</em></label>
          <input type="text" id="f-name" class="fi" placeholder="Alex Johnson">
        </div>
        <div class="fg">
          <label>Profile Type</label>
          <select id="f-type" class="fi">
            <option value="individual">👤 Individual / Founder</option>
            <option value="executive">💼 Executive / C-Suite</option>
            <option value="consultant">🤝 Consultant / Freelancer</option>
            <option value="creator">🎙 Creator / Speaker</option>
            <option value="corporate">🏢 Corporate Brand</option>
          </select>
        </div>
        <div class="fg">
          <label>Primary Goal</label>
          <select id="f-obj" class="fi">
            <option value="lead_generation">🎯 Generate Leads</option>
            <option value="personal_branding">🌟 Personal Branding</option>
            <option value="attract_investors">💰 Attract Investors</option>
            <option value="attract_talent">👥 Attract Talent</option>
            <option value="speaker_invites">🎤 Speaker Invites</option>
            <option value="job_search">💼 Job Search</option>
            <option value="corporate_brand">🏢 Corporate Brand</option>
          </select>
        </div>
        <div class="fg">
          <label>Industry <em>optional</em></label>
          <input type="text" id="f-industry" class="fi" placeholder="SaaS, Fintech, Marketing...">
        </div>
      </div>

      <div class="fg" style="margin-bottom:12px">
        <label>Target Audience <em>optional</em></label>
        <input type="text" id="f-audience" class="fi" placeholder="CTOs at B2B SaaS companies, Series A founders...">
      </div>

      <div class="fg" style="margin-bottom:20px">
        <label>Additional Context <em>optional</em></label>
        <textarea id="f-ctx" class="fta" placeholder="Any specific focus areas, current pain points, or context about this client..."></textarea>
      </div>

      <button class="go-btn" id="go-btn" onclick="runAnalysis()">
        <span>Analyze Profile with AI</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </button>
    </div>
  </section>

  <!-- ── LOADING ── -->
  <section class="loading-wrap hidden" id="loading-section">
    <div class="loading-card">
      <div class="spin-ring"><div></div><div></div></div>
      <div>
        <div class="load-title" id="load-title">Analyzing profile...</div>
        <div class="load-steps">
          <div class="lstep act" id="ls1">Scanning all 6 sections</div>
          <div class="lstep" id="ls2">Scoring profile elements</div>
          <div class="lstep" id="ls3">Generating AI recommendations</div>
          <div class="lstep" id="ls4">Building your report</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ── RESULTS ── -->
  <section class="results-wrap hidden" id="results">

    <div class="res-topbar">
      <div>
        <div class="res-url" id="res-url"></div>
        <div class="res-meta" id="res-meta"></div>
      </div>
      <div style="display:flex;align-items:center;gap:10px">
        <span class="prov-badge" id="prov-badge"></span>
        <button class="btn-new" onclick="resetForm()">← New Audit</button>
      </div>
    </div>

    <!-- Overall score -->
    <div class="score-card">
      <div class="score-ring-outer">
        <svg viewBox="0 0 120 120" class="score-svg">
          <circle class="score-bg-circle" cx="60" cy="60" r="52"/>
          <circle class="score-progress" id="score-progress" cx="60" cy="60" r="52"
            stroke-dasharray="326.73" stroke-dashoffset="326.73"
            transform="rotate(-90 60 60)"/>
        </svg>
        <div class="score-text">
          <div class="score-number" id="score-number">–</div>
          <div class="score-denom">/100</div>
        </div>
      </div>
      <div class="score-right">
        <div class="strength-tag" id="strength-tag">–</div>
        <div class="score-summary" id="score-summary"></div>
      </div>
    </div>

    <!-- Section bar chart -->
    <div class="bars-grid" id="bars-grid"></div>

    <!-- Top priorities -->
    <div class="block-hd">
      <div class="block-num">01</div>
      <div><h3>Top Priorities</h3><p>Most impactful changes — do these first</p></div>
    </div>
    <div class="priorities-list" id="priorities-list"></div>

    <!-- Quick wins -->
    <div class="block-hd" id="qw-hd" style="display:none">
      <div class="block-num">02</div>
      <div><h3>Quick Wins</h3><p>Changes under 10 minutes each</p></div>
    </div>
    <div class="qw-list" id="qw-list"></div>

    <!-- Section cards -->
    <div class="block-hd" style="margin-top:8px">
      <div class="block-num">03</div>
      <div><h3>Section Analysis</h3><p>Click any card for details and AI rewrite options</p></div>
    </div>
    <div class="cards-grid" id="cards-grid"></div>

  </section>

</main>

<!-- HISTORY -->
<div class="hist-bg hidden" id="hist-bg" onclick="toggleHistory()"></div>
<aside class="hist-panel hidden" id="hist-panel">
  <div class="hist-head">
    <h3>Audit History</h3>
    <button onclick="toggleHistory()">✕</button>
  </div>
  <div id="hist-list"></div>
</aside>

<!-- MODAL -->
<div class="modal-bg hidden" id="modal-bg" onclick="closeModal()">
  <div class="modal-box" onclick="event.stopPropagation()">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div id="modal-body"></div>
  </div>
</div>

<div class="toasts" id="toasts"></div>
<script src="/static/js/app.js"></script>
</body>
</html>
