from tools.claude_client import ask_claude

print("Test Connection ...")
try:
    reply = ask_claude("reply with just one world : OK")
    print("✅ Connection Success")
    print("Claude Reply:", reply)
except Exception as e:
    print("❌ Connection Error")
    print("  ", e)