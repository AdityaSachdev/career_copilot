# tools/memory_tools.py
"""
Memory Tools for Google ADK Root Agent.
Allows checking permanent SQLite memory at the start of a conversation.
"""
from google.adk.tools import ToolContext
from tools.memory_db import load_from_long_term_memory

def check_existing_career_profile(tool_context: ToolContext) -> str:
    """Checks permanent SQLite memory for an existing Master Profile.
    If found, loads it into the active session state so all sub-agents have access.
    """
    profile = load_from_long_term_memory("master_profile")
    if profile:
        # Load the permanent profile into this active session
        tool_context.state["master_profile"] = profile
        name = profile.get("name", "Candidate")
        headline = profile.get("headline", "")
        direct_skills = profile.get("direct_skills", [])
        return (
            f"Found saved permanent profile for {name} ({headline}). "
            f"Direct skills loaded ({len(direct_skills)}): {', '.join(direct_skills[:8])}..."
        )
    return "No saved profile found in permanent memory. The user should upload their resume, LinkedIn, or CV."
