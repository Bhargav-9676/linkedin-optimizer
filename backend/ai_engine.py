"""
ai_engine.py — AI calls using Groq (free) as primary provider
Reads API keys from config.py which loads from config.env
"""
import json
import urllib.request
import urllib.error
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from config import GROQ_API_KEY, GROQ_MODEL, ANTHROPIC_API_KEY, status as config_status


# ── GROQ CALL (PRIMARY - FREE) ──────────────────────────────────────────────
def call_groq(messages, max_tokens=2000, temperature=0.7):
    """
    Call Groq API - FREE tier: 6000 requests/day
    Model: llama3-8b-8192 (fast) or llama3-70b-8192 (better quality)
    Reads GROQ_API_KEY from config.env via config.py
    """
    cfg = config_status()
    if not cfg['groq']:
        return None, "Groq API key not configured in config.env"

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        return None, f"Groq HTTP {e.code}: {body[:200]}"
    except Exception as e:
        return None, str(e)


# ── CLAUDE CALL (OPTIONAL PAID FALLBACK) ────────────────────────────────────
def call_claude(messages, max_tokens=2000):
    if not ANTHROPIC_API_KEY:
        return None, "Claude API key not set"

    system_msg = next((m['content'] for m in messages if m['role'] == 'system'), '')
    user_msgs  = [m for m in messages if m['role'] != 'system']

    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": max_tokens,
        "system": system_msg,
        "messages": user_msgs
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data['content'][0]['text'], None
    except Exception as e:
        return None, str(e)


# ── SMART AI ROUTER ──────────────────────────────────────────────────────────
def call_ai(messages, max_tokens=2000, task="general"):
    """
    Routes to best available AI:
    1st: Groq (free, fast)
    2nd: Claude (paid, fallback)
    3rd: Template engine (always works)
    """
    # Try Groq first
    result, err = call_groq(messages, max_tokens)
    if result:
        return result, 'groq'

    # Try Claude if Groq fails
    if ANTHROPIC_API_KEY:
        result, err = call_claude(messages, max_tokens)
        if result:
            return result, 'claude'

    # Fallback to templates
    user_content = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
    return _template_fallback(user_content, task), 'template'


# ── TEMPLATE FALLBACK (ALWAYS FREE, ZERO API) ────────────────────────────────
def _template_fallback(prompt, task):
    # task-based routing takes priority over keyword matching
    if task == 'profile_audit':
        return _full_audit_template()
    prompt_l = prompt.lower()
    if task == 'section_rewrite' or 'rewrite' in prompt_l:
        # section-specific routing for rewrites
        if 'headline' in prompt_l:
            return '{"variations": ["Role | Who you help | Key outcome", "Title | Helping [audience] achieve [result]", "Founder | Solving [problem] for [ICP] | [Proof point]"], "best_pick": 0, "reason": "First variation follows the proven LinkedIn formula"}'
        if 'about' in prompt_l:
            return '{"rewritten": "I help [target audience] achieve [desired outcome].\n\nAfter [X years] in [industry], I noticed [key insight].\n\nHow I can help:\n\n→ [Outcome 1]\n→ [Outcome 2]\n→ [Outcome 3]\n\n[CTA: DM me or book a call]", "word_count": 75, "hook": "I help [target audience] achieve [desired outcome]."}'
        if 'experience' in prompt_l:
            return '{"rewritten": "Led [X]-person team to [specific result]\n• [Action verb] + [what you did] = [quantified result]\n• Built [system] that improved [outcome] by [X%]\n• Delivered [project] serving [X customers]", "bullets": ["Action + result", "Built system + outcome", "Delivered + impact"]}'
    if 'profile picture' in prompt_l or 'photo' in prompt_l:
        return _audit_template_response('profile_picture')
    if 'background' in prompt_l or 'banner' in prompt_l:
        return _audit_template_response('background_image')
    if 'about' in prompt_l or 'summary' in prompt_l:
        return _audit_template_response('about')
    if 'featured' in prompt_l:
        return _audit_template_response('featured')
    if 'experience' in prompt_l:
        return _audit_template_response('experience')
    if 'headline' in prompt_l:
        return _audit_template_response('headline')
    return _full_audit_template()


def _audit_template_response(section):
    templates = {
        'profile_picture': json.dumps({
            "score": 60, "status": "needs_work",
            "issues": ["Photo appears unprofessional or outdated", "Background is cluttered or distracting", "Image resolution may be too low"],
            "suggestions": ["Use a high-resolution headshot (400x400px minimum)", "Wear professional attire matching your industry", "Use a clean, solid or blurred background", "Smile — warm expressions increase connection rates by 40%", "Make sure your face fills 60-70% of the frame"],
            "example": "A crisp, well-lit headshot with a neutral background. Think LinkedIn profile pictures of top CEOs — professional yet approachable."
        }),
        'headline': json.dumps({
            "score": 55, "status": "needs_work",
            "issues": ["Headline is just a job title — misses opportunity to show value", "No mention of who you help or what outcome you create", "Not optimized for LinkedIn search keywords"],
            "suggestions": ["Follow this formula: [Role] | [Who you help] | [Key outcome/superpower]", "Include 2-3 industry keywords naturally", "Add a compelling hook or number if relevant", "Keep under 220 characters", "Avoid buzzwords like 'passionate', 'guru', 'ninja'"],
            "example": "Founder & CEO | Helping B2B SaaS teams cut churn by 30% | ex-Google | $50M+ revenue generated for clients"
        }),
        'background_image': json.dumps({
            "score": 40, "status": "needs_work",
            "issues": ["Default LinkedIn background or generic image", "No brand reinforcement or visual storytelling", "Missing opportunity to communicate value instantly"],
            "suggestions": ["Create a custom banner (1584x396px) with your brand colors", "Include your value proposition or tagline in text", "Add your website URL or a CTA", "Use Canva — they have free LinkedIn banner templates", "Ensure it complements your profile picture visually"],
            "example": "A branded banner showing your company logo, tagline, and one strong social proof statement — e.g., 'Trusted by 200+ companies across 12 countries'"
        }),
        'about': json.dumps({
            "score": 50, "status": "needs_work",
            "issues": ["About section reads like a resume, not a story", "First line doesn't hook the reader before 'see more' cutoff", "No clear call-to-action at the end", "Missing proof points or specific results"],
            "suggestions": ["Start with a bold first line that makes people click 'see more'", "Use the STORY framework: Situation → Challenge → Action → Result", "Add 3-5 quantified achievements (numbers build credibility)", "Write in first person — conversational, not corporate", "End with a clear CTA: 'DM me about X' or 'Email me at Y'", "Use line breaks and emojis sparingly for readability"],
            "example": "First line: 'I help founders go from invisible to inbound — without paid ads.'\nBody: Story of transformation + results.\nEnd CTA: 'If you want the same, send me a DM with the word GROW.'"
        }),
        'featured': json.dumps({
            "score": 35, "status": "needs_work",
            "issues": ["Featured section is empty or underutilized", "Missing lead magnets, case studies or social proof", "No content that drives action from profile visitors"],
            "suggestions": ["Add 3-5 Featured items: a lead magnet, best post, case study, website, or media mention", "First featured item should be your best lead-generation asset", "Include a link with a custom thumbnail and compelling title", "Feature your most viral or high-engagement LinkedIn post", "Add a newsletter sign-up or calendar booking link"],
            "example": "Item 1: Free guide PDF (lead magnet). Item 2: Your best LinkedIn post (10k+ impressions). Item 3: A client case study or press mention. Item 4: Your website or portfolio."
        }),
        'experience': json.dumps({
            "score": 65, "status": "average",
            "issues": ["Experience descriptions list duties, not achievements", "Missing quantified results and impact metrics", "No media attachments (presentations, videos, articles)", "Company descriptions don't explain context for unfamiliar brands"],
            "suggestions": ["Start each bullet with a strong action verb", "Add numbers: revenue generated, % growth, team size, projects delivered", "Use the CAR format: Challenge → Action → Result", "Attach relevant media to each role (presentations, articles, videos)", "Include 3-5 bullet points per role maximum — quality over quantity", "For lesser-known companies, add a brief description of what they do"],
            "example": "Instead of: 'Responsible for sales team'\nWrite: 'Led 8-person sales team to exceed $2.4M quarterly target — 127% of goal — by implementing account-based outreach strategy'"
        })
    }
    return templates.get(section, _full_audit_template())


def _full_audit_template():
    return json.dumps({
        "overall_score": 58,
        "profile_strength": "Intermediate",
        "summary": "Your LinkedIn profile has solid foundations but is missing key elements that drive inbound leads. The most impactful quick wins are rewriting your headline to show value, adding a hook to your About section, and activating your Featured section.",
        "sections": {
            "profile_picture": {
                "score": 65, "status": "average",
                "issues": ["Photo may not project the right professionalism level", "Background could be cleaner", "Image may not be optimized for LinkedIn crop"],
                "suggestions": ["Use a high-resolution headshot (400x400px minimum)", "Wear industry-appropriate attire", "Use a clean solid or blurred background", "Ensure face fills 60-70% of frame", "Smile naturally to boost connection rates"],
                "example": "Crisp, well-lit headshot with neutral background, direct eye contact, and a professional but approachable expression."
            },
            "headline": {
                "score": 50, "status": "needs_work",
                "issues": ["Headline only shows job title, misses value proposition", "No mention of who you help or what outcome you create", "Not optimized for LinkedIn search keywords"],
                "suggestions": ["Use formula: [Role] | [Who you help] | [Key outcome]", "Include 2-3 industry keywords naturally", "Add a specific result or number if available", "Keep under 220 characters", "Avoid buzzwords like passionate or results-driven"],
                "example": "Founder & CEO | Helping B2B SaaS teams cut churn by 30% | ex-Google | $50M+ revenue generated"
            },
            "background_image": {
                "score": 35, "status": "needs_work",
                "issues": ["Default LinkedIn background with zero brand communication", "Missing opportunity to show value proposition visually", "No website URL or call-to-action visible"],
                "suggestions": ["Create custom banner 1584x396px on Canva (free templates available)", "Include your tagline or value proposition as text overlay", "Add your website URL or booking link as a CTA", "Use your brand colors for visual consistency"],
                "example": "Branded banner with logo, tagline, social proof statement, and website URL in the corner."
            },
            "about": {
                "score": 55, "status": "needs_work",
                "issues": ["About section reads like a resume with no personal story", "First line does not hook reader before see-more cut-off", "No clear call-to-action at the end", "Missing quantified achievements and proof points"],
                "suggestions": ["Start with a bold hook that makes people click see more", "Use STORY format: Situation, Challenge, Action, Result", "Add 3-5 quantified achievements with real numbers", "Write in first person with conversational tone", "End with a specific CTA like DM me or Book a call"],
                "example": "First line: I help founders go from invisible to inbound without paid ads. Then share your story, add 3 proof points. Close with a clear CTA."
            },
            "featured": {
                "score": 30, "status": "needs_work",
                "issues": ["Featured section is empty or not used strategically", "Missing lead magnets, case studies, or social proof", "No content that converts profile visitors into leads"],
                "suggestions": ["Add 3-5 Featured items: lead magnet, best post, case study, website", "First featured item should be your top lead-gen asset", "Include a newsletter signup or calendar booking link", "Feature your most viral or high-engagement post", "Add a press mention or media appearance if available"],
                "example": "Item 1: Free PDF guide. Item 2: Best LinkedIn post with 10k+ impressions. Item 3: Client case study. Item 4: Website or portfolio link."
            },
            "experience": {
                "score": 70, "status": "average",
                "issues": ["Descriptions list job duties instead of accomplishments", "Missing quantified results and impact metrics", "No media attachments to add visual credibility"],
                "suggestions": ["Start every bullet with a strong action verb: Led, Built, Grew, Launched", "Add numbers for revenue, growth percentage, team size, delivery count", "Use CAR format: Challenge, Action, Result", "Attach media to each role: presentations, articles, screenshots", "Keep to 3-4 bullets per role, quality over quantity"],
                "example": "Before: Responsible for managing the sales team. After: Led 8-person sales team to 127% of $2.4M quarterly target by introducing account-based outreach framework."
            }
        },
        "top_priorities": [
            "Rewrite headline using value proposition formula: Role | Who you help | Key outcome",
            "Add a compelling hook as the first line of your About section",
            "Create and upload a branded background banner on Canva (free tool)",
            "Add 3 Featured items: a lead magnet, your best post, and your website",
            "Update top 2 experience roles with quantified achievements and results"
        ],
        "quick_wins": [
            "Add your website URL to the contact info section (takes 1 minute)",
            "Turn on Creator Mode to unlock more profile features (takes 2 minutes)",
            "Add 5 relevant skills to improve search visibility (takes 5 minutes)"
        ]
    })

def analyze_linkedin_profile(linkedin_url, client_name="", client_type="individual",
                              additional_context="", objective="lead_generation"):
    """
    Main function: given a LinkedIn URL, return full AI audit with scores and suggestions.
    Uses Groq API (from config.env) as primary AI.
    """
    # Extract username/handle from URL for context
    url_parts = linkedin_url.rstrip('/').split('/')
    handle = url_parts[-1] if url_parts else linkedin_url

    objective_context = {
        'lead_generation':  'generating inbound leads and client inquiries',
        'personal_branding': 'building a strong personal brand and thought leadership',
        'corporate_brand':   'building corporate brand awareness and credibility',
        'attract_investors': 'attracting investors and funding opportunities',
        'attract_talent':    'attracting top talent and building employer brand',
        'speaker_invites':   'getting speaker invitations and media opportunities',
        'job_search':        'standing out to recruiters and landing a job'
    }.get(objective, 'LinkedIn growth')

    system_prompt = """You are a world-class LinkedIn profile strategist who has optimized 500+ profiles for founders, executives, and brands. You provide brutally honest, specific, and actionable feedback.

Your analysis must be returned as VALID JSON only — no markdown, no explanation outside JSON.

For each section, give:
- A score (0-100)
- Status: "strong" (80+), "average" (50-79), "needs_work" (below 50)
- 2-4 specific issues found
- 3-5 concrete, actionable suggestions
- A short "example" showing what good looks like

Be specific. Avoid generic advice. Reference LinkedIn best practices, algorithm factors, and conversion psychology."""

    user_prompt = f"""Analyze this LinkedIn profile and provide a comprehensive audit:

Profile URL: {linkedin_url}
LinkedIn Handle/Username: {handle}
Client Name: {client_name or 'Not provided'}
Profile Type: {client_type} (individual person or corporate brand)
Primary Objective: {objective_context}
Additional Context: {additional_context or 'None provided'}

Return a JSON audit with this EXACT structure:
{{
  "overall_score": <number 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "profile_strength": "<Beginner|Intermediate|Advanced|Expert>",
  "sections": {{
    "profile_picture": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["<specific issue 1>", "<specific issue 2>"],
      "suggestions": ["<actionable suggestion 1>", "<actionable suggestion 2>", "<actionable suggestion 3>"],
      "example": "<what a great version looks like>"
    }},
    "headline": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["..."],
      "suggestions": ["..."],
      "example": "<example headline for this person's goal>"
    }},
    "background_image": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["..."],
      "suggestions": ["..."],
      "example": "..."
    }},
    "about": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["..."],
      "suggestions": ["..."],
      "example": "<first 2 lines of a great About section for this person>"
    }},
    "featured": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["..."],
      "suggestions": ["..."],
      "example": "..."
    }},
    "experience": {{
      "score": <0-100>,
      "status": "<strong|average|needs_work>",
      "issues": ["..."],
      "suggestions": ["..."],
      "example": "<rewritten bullet point showing quantified achievement>"
    }}
  }},
  "top_priorities": [
    "<most impactful change to make first>",
    "<second priority>",
    "<third priority>",
    "<fourth priority>",
    "<fifth priority>"
  ],
  "quick_wins": [
    "<change that takes less than 10 minutes>",
    "<another quick win>",
    "<another quick win>"
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]

    raw_result, provider = call_ai(messages, max_tokens=2500, task='profile_audit')

    # Parse JSON from result
    try:
        # Strip any markdown code fences if present
        clean = raw_result.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[-1]
            clean = clean.rsplit('```', 1)[0]
        audit_data = json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract JSON from within the text
        try:
            start = raw_result.find('{')
            end   = raw_result.rfind('}') + 1
            if start >= 0 and end > start:
                audit_data = json.loads(raw_result[start:end])
            else:
                audit_data = json.loads(_full_audit_template())
                provider = 'template'
        except:
            audit_data = json.loads(_full_audit_template())
            provider = 'template'

    return audit_data, provider


# ── SECTION REWRITER ─────────────────────────────────────────────────────────
def rewrite_section(section_name, current_content, client_name, objective, industry, target_audience):
    """AI rewrites a specific section (headline, about, etc.) for the client."""
    section_prompts = {
        'headline': f"""Rewrite this LinkedIn headline for maximum impact.
Current headline: "{current_content}"
Person: {client_name}
Goal: {objective}
Industry: {industry}
Target audience: {target_audience}

Write 3 headline variations. Each should follow the formula: [Role] | [Who you help] | [Key outcome or differentiator]
Keep each under 220 characters. Return JSON: {{"variations": ["...", "...", "..."], "best_pick": 0, "reason": "..."}}""",

        'about': f"""Rewrite this LinkedIn About section to be compelling and conversion-focused.
Current about: "{current_content or 'Empty / not provided'}"
Person: {client_name}
Goal: {objective}
Industry: {industry}
Target audience: {target_audience}

Write a complete About section that:
- Opens with a BOLD hook (first line must make them click 'see more')
- Tells a transformation story
- Includes 3 quantified proof points (use placeholders like [X%] if unknown)
- Ends with a clear CTA
- Uses line breaks for readability
- Max 2600 characters

Return JSON: {{"rewritten": "...", "word_count": N, "hook": "first line here"}}""",

        'experience': f"""Improve this LinkedIn experience description to show impact and results.
Current text: "{current_content or 'Empty / not provided'}"
Industry: {industry}

Rewrite with:
- Strong action verbs
- Quantified results (use [X] placeholders where numbers unknown)
- CAR format: Challenge → Action → Result
- 3-4 bullet points max

Return JSON: {{"rewritten": "...", "bullets": ["...", "...", "..."]}}"""
    }

    prompt = section_prompts.get(section_name, f"Improve this LinkedIn {section_name} section: {current_content}")
    messages = [
        {"role": "system", "content": "You are a LinkedIn copywriting expert. Return only valid JSON. Be specific and compelling."},
        {"role": "user",   "content": prompt}
    ]

    raw, provider = call_ai(messages, max_tokens=1500)
    try:
        clean = raw.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[-1].rsplit('```', 1)[0]
        return json.loads(clean), provider
    except:
        return {"rewritten": raw, "provider": provider}, provider
