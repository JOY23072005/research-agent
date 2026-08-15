from langgraph.graph import StateGraph, START, END

from agent.state import ResearchState


def initialize(state: ResearchState):
    """
    Initialize the research state.
    """

    print("Initializing research...")

    return {
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


def build_graph():

    graph = StateGraph(ResearchState)

    # Add node
    graph.add_node("initialize", initialize)

    # START → initialize
    graph.add_edge(START, "initialize")

    # initialize → END
    graph.add_edge("initialize", END)

    return graph.compile()


research_graph = build_graph()