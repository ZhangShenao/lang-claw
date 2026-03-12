"""Personal data sub-agent definition."""

from app.tools.personal_tools import build_personal_tools

PERSONAL_DATA_PROMPT = """
You are the personal-data specialist for Lang Claw.

Use the available tools to read or update the user's profile and tasks.
Return concise, structured facts back to the main agent.
""".strip()


def build_personal_data_agent(user_id: str) -> dict:
    """Build the personal-data sub-agent definition.

    Args:
        user_id: The user identifier for personal data operations.

    Returns:
        Sub-agent definition dict.
    """
    return {
        "name": "personal-data",
        "description": "Handles saved profile data, preferences, and user tasks.",
        "system_prompt": PERSONAL_DATA_PROMPT,
        "tools": build_personal_tools(user_id),
    }
