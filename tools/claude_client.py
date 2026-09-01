from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS, validate_config

def ask_claude(prompt, system=None):
    validate_config()
    client = Anthropic()

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