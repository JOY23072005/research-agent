from langgraph.graph import StateGraph, START, END

from agent.state import ResearchState
from agent.executor import execute_research_plan
from agent.prompts import RESEARCH_PLANNER_PROMPT
from agent.analyzer import analyze_research

from llm import get_llm
from schemas import ResearchPlan


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


def plan_research(state: ResearchState):
    """
    Ask the NVIDIA LLM to create a research plan.
    """

    print("\nPlanning research...")

    llm = get_llm()

    planner = llm.with_structured_output(ResearchPlan)

    prompt = f"""
{RESEARCH_PLANNER_PROMPT}

User query:

{state["query"]}

Available tools:

- web_search
- fetch_page

Create the initial research plan.
"""

    plan = planner.invoke(prompt)

    print("\nResearch plan:")
    print(plan.model_dump_json(indent=2))

    return {
        "research_plan": [
            step.model_dump()
            for step in plan.steps
        ]
    }


def execute_tools(state: ResearchState):
    """
    Execute the tools selected by the LLM.
    """

    print("\nExecuting research plan...")

    results = execute_research_plan(
        state["research_plan"]
    )

    return {
        "tool_results": results,

        "tools_executed": [
            result["tool"]
            for result in results
            if result.get("success")
        ],
    }


def build_graph():

    graph = StateGraph(ResearchState)

    graph.add_node("initialize", initialize)
    graph.add_node("plan_research", plan_research)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("analyze_research",analyze_research)

    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "plan_research")
    graph.add_edge("plan_research", "execute_tools")
    graph.add_edge("execute_tools","analyze_research")

    graph.add_edge("analyze_research",END)

    return graph.compile()


research_graph = build_graph()