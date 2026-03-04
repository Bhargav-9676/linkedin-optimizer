#!/usr/bin/env python3
"""
run.py — Start the LinkedIn Profile Optimizer
Usage: python3 run.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import init_db
from config   import FLASK_PORT, FLASK_DEBUG, status as cfg_status
from app      import app

if __name__ == '__main__':
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   LinkedIn Profile Optimizer  v1.0           ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    init_db()

    s = cfg_status()
    print("  AI Provider Status:")
    if s['groq']:
        print(f"  ✅  Groq API    — READY   (model: {s['model']})")
    else:
        print("  ⚠️   Groq API    — NOT SET  (add key to config.env)")
    if s['claude']:
        print("  ✅  Claude API  — READY   (paid fallback)")
    else:
        print("  —   Claude API  — not set (optional)")

    print()
    print("  📁 API keys file:  ./config.env")
    print("  💡 Free Groq key:  https://console.groq.com")
    print()
    print(f"  🌐 Open:  http://localhost:{FLASK_PORT}")
    print()

    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
