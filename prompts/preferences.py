import os

from config import DATA_DIR

PREFERENCES_PATH = os.path.join(DATA_DIR, "preferences.txt")

# The candidate's own filters: what they will and will not accept, regardless
# of how well the skills match. This is the most personal part of the system,
# so it belongs to the user rather than the code. Leave it empty to apply no
# hard constraints at all and decide on skills alone.
DEFAULT_PREFERENCES = """1. The job must be fully Remote. Exclude Hybrid and On-site roles.
2. The company/role location must be within: Europe, North America, or the \
Gulf countries (GCC).
3. Exclude any job based in: X Country."""


def load_preferences() -> str:
    """Return the stored preferences, writing the defaults on first use."""
    if not os.path.exists(PREFERENCES_PATH):
        save_preferences(DEFAULT_PREFERENCES)
        return DEFAULT_PREFERENCES

    with open(PREFERENCES_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_preferences(text: str) -> None:
    """Persist the preferences so they load automatically next time."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PREFERENCES_PATH, "w", encoding="utf-8") as f:
        f.write(text.strip())


def reset_preferences() -> str:
    """Restore and return the default preferences."""
    save_preferences(DEFAULT_PREFERENCES)
    return DEFAULT_PREFERENCES
