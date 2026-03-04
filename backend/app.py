"""
app.py — Flask backend for LinkedIn Profile Optimizer
All API keys come from config.env via config.py
"""
import json
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder="../frontend/static")

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")

sys.path.insert(0, os.path.dirname(__file__))
from config import FLASK_PORT, FLASK_DEBUG, SECRET_KEY, status as config_status
from database import init_db, get_db, row_to_dict, rows_to_list
from ai_engine import analyze_linkedin_profile, rewrite_section

# ── APP SETUP ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
    static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
    template_folder=os.path.join(BASE_DIR, 'frontend'))

app.config['SECRET_KEY'] = SECRET_KEY


@app.after_request
def cors(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    r.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return r

@app.route('/api/<path:p>', methods=['OPTIONS'])
def opts(p): return jsonify({}), 200


# ── FRONTEND ─────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── HEALTH / STATUS ──────────────────────────────────────────────────────────
@app.route('/api/status')
def api_status():
    cfg = config_status()
    return jsonify({
        'ok': True,
        'ai': {
            'groq_ready':   cfg['groq'],
            'claude_ready': cfg['claude'],
            'model':        cfg['model'],
            'provider':     'groq' if cfg['groq'] else ('claude' if cfg['claude'] else 'template'),
        },
        'version': '1.0.0'
    })


# ── AUDIT: Analyze Profile ────────────────────────────────────────────────────
@app.route('/api/audit', methods=['POST'])
def create_audit():
    """
    POST /api/audit
    Body: { linkedin_url, client_name, client_type, objective, industry, target_audience, additional_context }
    Returns: full audit JSON with scores and suggestions
    """
    d = request.get_json() or {}
    url = (d.get('linkedin_url') or '').strip()

    if not url:
        return jsonify({'error': 'LinkedIn URL is required'}), 400

    # Normalize URL
    if not url.startswith('http'):
        url = 'https://' + url
    if 'linkedin.com' not in url:
        return jsonify({'error': 'Please provide a valid LinkedIn profile URL'}), 400

    client_name    = d.get('client_name', '').strip()
    client_type    = d.get('client_type', 'individual')
    objective      = d.get('objective', 'lead_generation')
    industry       = d.get('industry', '').strip()
    target_audience = d.get('target_audience', '').strip()
    additional_ctx = d.get('additional_context', '').strip()

    # Run AI audit
    try:
        audit_data, provider = analyze_linkedin_profile(
            url, client_name, client_type, additional_ctx, objective
        )
    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500

    # Persist to SQLite
    overall_score = audit_data.get('overall_score', 0)
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO audits (linkedin_url, client_name, client_type, raw_input, audit_json, overall_score, ai_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (url, client_name, client_type,
              json.dumps({'objective': objective, 'industry': industry, 'target_audience': target_audience}),
              json.dumps(audit_data), overall_score, provider))
        audit_id = cur.lastrowid

        # Store each section
        sections = audit_data.get('sections', {})
        for section_name, section_data in sections.items():
            conn.execute("""
                INSERT INTO profile_sections (audit_id, section, score, status, issues, suggestions, example)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (audit_id, section_name,
                  section_data.get('score', 0),
                  section_data.get('status', 'needs_work'),
                  json.dumps(section_data.get('issues', [])),
                  json.dumps(section_data.get('suggestions', [])),
                  section_data.get('example', '')))

    return jsonify({
        'success': True,
        'audit_id': audit_id,
        'audit': audit_data,
        'ai_provider': provider,
        'linkedin_url': url,
        'analyzed_at': datetime.now().isoformat()
    })


# ── REWRITE: AI rewrites a specific section ───────────────────────────────────
@app.route('/api/audit/<int:audit_id>/rewrite', methods=['POST'])
def rewrite_audit_section(audit_id):
    """
    POST /api/audit/:id/rewrite
    Body: { section, current_content, objective, industry, target_audience }
    Returns: AI-rewritten content for that section
    """
    d = request.get_json() or {}
    section = d.get('section', '').strip()

    if section not in ['headline', 'about', 'experience']:
        return jsonify({'error': 'Rewrite supported for: headline, about, experience'}), 400

    with get_db() as conn:
        audit = row_to_dict(conn.execute("SELECT * FROM audits WHERE id=?", (audit_id,)).fetchone())
    if not audit:
        return jsonify({'error': 'Audit not found'}), 404

    raw_input = json.loads(audit.get('raw_input') or '{}')
    rewritten, provider = rewrite_section(
        section,
        d.get('current_content', ''),
        audit.get('client_name', ''),
        raw_input.get('objective', 'lead_generation'),
        d.get('industry') or raw_input.get('industry', ''),
        d.get('target_audience') or raw_input.get('target_audience', '')
    )

    # Save rewrite history
    with get_db() as conn:
        conn.execute("""
            INSERT INTO rewrite_history (audit_id, section, original, rewritten, ai_provider)
            VALUES (?, ?, ?, ?, ?)
        """, (audit_id, section, d.get('current_content', ''), json.dumps(rewritten), provider))

    return jsonify({'success': True, 'section': section, 'result': rewritten, 'ai_provider': provider})


# ── GET AUDIT HISTORY ────────────────────────────────────────────────────────
@app.route('/api/audits', methods=['GET'])
def get_audits():
    with get_db() as conn:
        audits = rows_to_list(conn.execute(
            "SELECT id,linkedin_url,client_name,client_type,overall_score,ai_provider,created_at FROM audits ORDER BY created_at DESC LIMIT 50"
        ).fetchall())
    return jsonify(audits)


@app.route('/api/audit/<int:audit_id>', methods=['GET'])
def get_audit(audit_id):
    with get_db() as conn:
        audit = row_to_dict(conn.execute("SELECT * FROM audits WHERE id=?", (audit_id,)).fetchone())
        if not audit:
            return jsonify({'error': 'Not found'}), 404
        sections = rows_to_list(conn.execute(
            "SELECT * FROM profile_sections WHERE audit_id=?", (audit_id,)).fetchall())
        rewrites = rows_to_list(conn.execute(
            "SELECT * FROM rewrite_history WHERE audit_id=? ORDER BY created_at DESC", (audit_id,)).fetchall())
    audit['audit_data'] = json.loads(audit.get('audit_json') or '{}')
    audit['sections']   = sections
    audit['rewrites']   = rewrites
    return jsonify(audit)


@app.route('/api/audit/<int:audit_id>', methods=['DELETE'])
def delete_audit(audit_id):
    with get_db() as conn:
        conn.execute("DELETE FROM audits WHERE id=?", (audit_id,))
    return jsonify({'success': True})


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    cfg = config_status()
    print("\n" + "="*52)
    print("  LinkedIn Profile Optimizer — Backend Ready")
    print("="*52)
    print(f"  Groq API:   {'✅ Configured' if cfg['groq'] else '⚠️  Not set (add key to config.env)'}")
    print(f"  Claude API: {'✅ Configured' if cfg['claude'] else '— Not set (optional)'}")
    print(f"  Model:      {cfg['model']}")
    print(f"  URL:        http://localhost:{FLASK_PORT}")
    print("="*52 + "\n")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
