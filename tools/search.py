from ddgs import DDGS


def web_search(
    query: str,
    max_results: int = 10,
    region: str = "in-en",
) -> dict:
    """
    Search the public web and return normalized JSON.
    """

    try:
        with DDGS(timeout=15) as ddgs:
            results = list(
                ddgs.text(
                    query,
                    region=region,
                    safesearch="moderate",
                    max_results=max_results,
                )
            )

        normalized = []

        for result in results:
            normalized.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body"),
            })

        return {
            "success": True,
            "query": query,
            "results": normalized,
        }

    except Exception as exc:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": str(exc),
        }