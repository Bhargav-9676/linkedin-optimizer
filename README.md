# LinkedIn Profile Optimizer

AI-powered LinkedIn profile audit tool.
Analyzes 6 profile sections and gives specific recommendations.

**Backend**: Python + Flask + SQLite  
**Frontend**: HTML + CSS + JS  
**AI**: Groq API (free) as primary — llama3-8b

---

## Quick Start

### 1. Add your Groq API key
Open `config.env` and replace the placeholder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a **free** key at → https://console.groq.com  
No credit card. 6000 requests/day free.

### 2. Run the app
```bash
python3 run.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## Project Structure

```
linkedin_profile_optimizer/
│
├── config.env              ← 🔑 API keys go HERE (never commit this)
├── run.py                  ← Start the app
│
├── backend/
│   ├── app.py              ← Flask routes
│   ├── ai_engine.py        ← Groq API calls + fallback templates
│   ├── config.py           ← Reads keys from config.env
│   └── database.py         ← SQLite setup
│
├── database/
│   └── optimizer.db        ← Auto-created on first run
│
└── frontend/
    ├── index.html
    └── static/
        ├── css/style.css
        └── js/app.js
```

---

## How config.env works

`config.env` is the single place for all API keys.  
`backend/config.py` reads it automatically — no `.env` library needed.

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxx        ← Primary AI (free)
GROQ_MODEL=llama3-8b-8192            ← Model choice
ANTHROPIC_API_KEY=                   ← Optional paid fallback
```

All backend modules import from `config.py`:
```python
from config import GROQ_API_KEY, GROQ_MODEL
```

---

## What gets analyzed

| Section | What AI checks |
|---|---|
| Profile Picture | Professionalism, lighting, framing |
| Headline | Value proposition, keywords, formula |
| Background Image | Branding, CTA, visual communication |
| About Section | Hook, story, proof points, CTA |
| Featured Section | Lead magnets, best content, conversions |
| Experience | Results vs duties, numbers, impact |
