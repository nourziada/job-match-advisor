from tools.claude_client import ask_claude

print("Test Connection ...")
try:
    reply = ask_claude("reply with just one world : OK")
    print("[OK] Connection Success")
    print("Claude Reply:", reply)
except Exception as e:
    print("[ERROR] Connection Error")
    print("  ", e)