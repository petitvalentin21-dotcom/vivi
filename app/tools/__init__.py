from app.tools.registry import REGISTRY, ToolDefinition, get_tool, list_tools, register_tool
from app.tools.api import router

# Side-effect import: registers all 5 tools into REGISTRY
from app.tools import meals_tools  # noqa: F401

__all__ = ["REGISTRY", "ToolDefinition", "list_tools", "get_tool", "register_tool", "router"]
