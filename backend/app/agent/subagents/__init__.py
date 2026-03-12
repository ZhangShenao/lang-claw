"""Sub-agents package.

Each sub-agent is defined in its own module and exported here for easy import.
"""

from app.agent.subagents.deep_research import build_deep_research_agent
from app.agent.subagents.personal_data import build_personal_data_agent

__all__ = [
    "build_deep_research_agent",
    "build_personal_data_agent",
]
