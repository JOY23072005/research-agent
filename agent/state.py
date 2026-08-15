from typing import TypedDict, Any


class ResearchState(TypedDict):
    query: str
    entity: dict[str, Any]

    research_round: int
    max_research_rounds: int

    tools_executed: list[str]
    tool_results: list[dict[str, Any]]

    sources: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    claims: list[dict[str, Any]]

    missing_fields: list[str]
    contradictions: list[dict[str, Any]]

    research_plan: list[dict[str, Any]]

    entity_valid: bool

    next_research_required: bool

    validation_passed: bool
    validation_errors: list[str]

    final_result: dict[str, Any] | None