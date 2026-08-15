from llm import get_llm
from schemas import ResearchPlan


llm = get_llm()

planner = llm.with_structured_output(ResearchPlan)

result = planner.invoke(
    """
    You are an OSINT research planner.

    Create an initial research plan for:

    "Research NVIDIA"

    Available tools:

    - web_search
    - fetch_page
    - crawl
    - browse
    - extract_page
    - whois
    - dns
    - username_search
    - email_search
    - github_search
    - verify_entity
    - verify_claim

    Select only tools that are useful for the investigation.

    Return the research plan as structured data.
    """
)

print(result.model_dump_json(indent=2))