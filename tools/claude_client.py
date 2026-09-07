from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS, validate_config

def ask_claude(prompt, system=None):
    validate_config()
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    params = {
        "model": CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "disabled"},
    }

    if system:
        params["system"] = system

    response  = client.messages.create(**params)

    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


_client = None

def get_client():
    """يرجّع نسخة واحدة من الـ client لإعادة استخدامها (بدل إنشائها كل مرة)."""
    global _client
    if _client is None:
        validate_config()
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client