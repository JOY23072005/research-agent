from agent.state import ResearchState


state: ResearchState = {
    "query": "Research ABC Technologies",

    "entity": {},

    "research_round": 0,

    "max_research_rounds": 5,

    "tools_executed": [],

    "tool_results": [],

    "sources": [],

    "findings": [],

    "claims": [],

    "missing_fields": [],

    "contradictions": [],

    "research_plan": [],

    "entity_valid": False,

    "validation_passed": False,

    "validation_errors": [],

    "final_result": None,
}

print(state)