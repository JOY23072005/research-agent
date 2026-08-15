from agent.prompts import RESEARCH_ANALYZER_PROMPT
from agent.state import ResearchState

from llm import get_llm
from schemas import ResearchAnalysis


def analyze_research(state: ResearchState):
    """
    Analyze all results collected so far.
    """

    print("\nAnalyzing research results...")

    llm = get_llm()

    analyzer = llm.with_structured_output(
        ResearchAnalysis
    )

    prompt = f"""
{RESEARCH_ANALYZER_PROMPT}

Original user query:

{state["query"]}

Previously collected findings:

{state["findings"]}

Previously discovered sources:

{state["sources"]}

Tool results:

{state["tool_results"]}
"""

    analysis = analyzer.invoke(prompt)

    print("\nResearch analysis:")
    print(
        analysis.model_dump_json(indent=2)
    )

    return {
        "findings": [
            finding.model_dump()
            for finding in analysis.findings
        ],

        "missing_fields": analysis.missing_fields,

        "contradictions": [
            contradiction.model_dump()
            for contradiction in analysis.contradictions
        ],

        "next_research_required": analysis.next_research_required,
    }