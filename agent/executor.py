from typing import Any

from tools.registry import get_tool

def contains_placeholder(value):
    if isinstance(value, str):
        return (
            "{{" in value
            or "}}" in value
        )

    if isinstance(value, dict):
        return any(
            contains_placeholder(v)
            for v in value.values()
        )

    if isinstance(value, list):
        return any(
            contains_placeholder(v)
            for v in value
        )

    return False

def execute_research_plan(
    research_plan: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Execute the tools requested by the LLM research plan.

    Each step in the plan must contain:
        {
            "tool": "tool_name",
            "input": {...}
        }

    Returns a list of normalized tool execution results.
    """

    results = []

    for step in research_plan:

        tool_name = step.get("tool")
        tool_input = step.get("input", {})

        if contains_placeholder(tool_input):

            results.append({
                "success": False,
                "tool": tool_name,
                "input": tool_input,
                "error": (
                    "Tool input contains an unresolved "
                    "placeholder."
                ),
            })

            continue

        if not tool_name:
            results.append({
                "success": False,
                "tool": None,
                "input": tool_input,
                "error": "Missing tool name."
            })
            continue

        tool = get_tool(tool_name)

        if tool is None:
            results.append({
                "success": False,
                "tool": tool_name,
                "input": tool_input,
                "error": f"Unknown tool: {tool_name}"
            })
            continue

        try:
            result = tool(**tool_input)

            results.append({
                "success": True,
                "tool": tool_name,
                "input": tool_input,
                "result": result,
            })

        except Exception as exc:
            results.append({
                "success": False,
                "tool": tool_name,
                "input": tool_input,
                "error": str(exc),
            })

    return results