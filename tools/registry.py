from tools.search import web_search
from tools.browser import fetch_page
from tools.extractor import extract_page


TOOLS = {
    "web_search": {
        "function": web_search,
        "description": (
            "Search the public web for information about "
            "a person, business, organization, domain, "
            "product, or website."
        ),
    },

    "fetch_page": {
        "function": fetch_page,
        "description": (
            "Open a webpage using a real browser and return "
            "the page URL, HTTP status, title, visible text, "
            "and discovered links."
        ),
    },

    "extract_page": {
        "function": extract_page,
        "description": (
            "Extract structured information from a fetched "
            "webpage including emails, phone numbers, prices, "
            "social-media links, and policy links."
        ),
    },
}


def get_tool(name: str):
    tool = TOOLS.get(name)

    if not tool:
        return None

    return tool["function"]


def get_tool_descriptions():
    return {
        name: tool["description"]
        for name, tool in TOOLS.items()
    }


def list_tools():
    return list(TOOLS.keys())