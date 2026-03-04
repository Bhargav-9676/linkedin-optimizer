"""
config.py — Loads all API keys and settings from config.env
This is the SINGLE source of truth for all credentials.
Import this anywhere: from config import GROQ_API_KEY, GROQ_MODEL
"""
import os

# ── Locate the config.env file ─────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BASE_DIR, 'config.env')


def _load_env(filepath):
    """Parse key=value lines from config.env into a dict."""
    env = {}
    if not os.path.exists(filepath):
        print(f"[CONFIG] Warning: {filepath} not found. Using environment variables.")
        return env
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                env[key.strip()] = value.strip()
    return env


# Load the env file
_env = _load_env(_ENV_FILE)


def get(key, default=''):
    """Get a config value: checks config.env first, then OS environment."""
    return _env.get(key) or os.environ.get(key, default)


# ── Exported constants ──────────────────────────────────────
GROQ_API_KEY      = get('GROQ_API_KEY')
GROQ_MODEL        = get('GROQ_MODEL', 'llama3-8b-8192')
ANTHROPIC_API_KEY = get('ANTHROPIC_API_KEY')
FLASK_PORT        = int(get('FLASK_PORT', '5000'))
FLASK_DEBUG       = get('FLASK_DEBUG', 'true').lower() == 'true'
SECRET_KEY        = get('SECRET_KEY', 'linkedin-optimizer-secret')

# ── Status helper ───────────────────────────────────────────
def status():
    """Return which AI providers are configured."""
    return {
        'groq':   bool(GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here'),
        'claude': bool(ANTHROPIC_API_KEY),
        'model':  GROQ_MODEL,
    }


if __name__ == '__main__':
    s = status()
    print("=== Config Status ===")
    print(f"Groq configured:   {s['groq']}  (model: {s['model']})")
    print(f"Claude configured: {s['claude']}")
    print(f"Config file:       {_ENV_FILE}")
