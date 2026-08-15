from ddgs import DDGS


def web_search(
    query: str,
    max_results: int = 10,
    region: str = "in-en",
) -> dict:
    """
    Search the public web and return normalized results.
    """

    try:
        with DDGS(timeout=10) as ddgs:
            results = list(
                ddgs.text(
                    query,
                    region=region,
                    safesearch="moderate",
                    max_results=max_results,
                )
            )

        normalized_results = []

        for result in results:
            normalized_results.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body"),
            })

        return {
            "success": True,
            "query": query,
            "results": normalized_results,
        }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": str(e),
        }