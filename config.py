import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env by absolute path, not from the current working directory, so the
# keys are found when the MCP server is launched by Claude Desktop from
# somewhere else.
load_dotenv(os.path.join(BASE_DIR, ".env"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
CV_DIR = os.getenv("CV_PATH")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-4")

DATA_DIR = os.path.join(BASE_DIR, "data")
CV_DIR = os.path.join(DATA_DIR, "cv")

def validate_config():
    if not ANTHROPIC_API_KEY or not ANTHROPIC_API_KEY.startswith("sk-ant-"):
        raise ValueError(
            "ANTHROPIC_API_KEY ERROR"
        )