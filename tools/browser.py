from playwright.sync_api import sync_playwright


def fetch_page(
    url: str,
    timeout: int = 30000,
) -> dict:
    """
    Open a webpage using Playwright and return useful page information.
    """

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=timeout,
            )

            page.wait_for_load_state(
                "domcontentloaded"
            )

            title = page.title()

            text = page.locator(
                "body"
            ).inner_text(
                timeout=10000
            )

            links = page.locator(
                "a"
            ).evaluate_all(
                """
                elements => elements.map(a => ({
                    text: a.innerText,
                    href: a.href
                }))
                """
            )

            result = {
                "success": True,
                "url": page.url,
                "status_code": (
                    response.status
                    if response
                    else None
                ),
                "title": title,
                "text": text,
                "links": links,
            }

            browser.close()

            return result

    except Exception as exc:

        return {
            "success": False,
            "url": url,
            "error": str(exc),
        }