import re
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"
)

PRICE_PATTERN = re.compile(
    r"(?:₹|Rs\.?|INR|\$|USD|€|EUR|£|GBP)\s?"
    r"(?:\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\.\d{1,2})?"
)


SOCIAL_DOMAINS = {
    "instagram.com": "instagram",
    "facebook.com": "facebook",
    "linkedin.com": "linkedin",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "youtube.com": "youtube",
    "tiktok.com": "tiktok",
    "pinterest.com": "pinterest",
}


POLICY_KEYWORDS = {
    "shipping": [
        "shipping",
        "delivery",
        "shipping-policy",
        "delivery-policy",
    ],
    "terms": [
        "terms",
        "terms-of-use",
        "terms-and-conditions",
        "terms-conditions",
    ],
    "privacy": [
        "privacy",
        "privacy-policy",
    ],
    "refund": [
        "refund",
        "return",
        "returns",
        "return-policy",
        "refund-policy",
    ],
}


def _extract_emails(text: str) -> list[str]:
    return sorted(set(
        EMAIL_PATTERN.findall(text or "")
    ))


def _extract_phones(text: str) -> list[str]:
    matches = PHONE_PATTERN.findall(text or "")

    cleaned = []

    for phone in matches:
        phone = re.sub(r"\s+", " ", phone).strip()

        # Avoid treating extremely long numeric strings as phones.
        digits = re.sub(r"\D", "", phone)

        if 8 <= len(digits) <= 15:
            cleaned.append(phone)

    return sorted(set(cleaned))


def _extract_prices(text: str) -> list[str]:
    return sorted(set(
        PRICE_PATTERN.findall(text or "")
    ))


def _classify_social_url(url: str) -> str | None:
    try:
        hostname = urlparse(url).netloc.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        for domain, platform in SOCIAL_DOMAINS.items():
            if hostname == domain or hostname.endswith("." + domain):
                return platform

    except Exception:
        pass

    return None


def _extract_social_links(links: list[dict]) -> list[dict]:
    results = []

    for link in links:
        url = link.get("href")

        if not url:
            continue

        platform = _classify_social_url(url)

        if platform:
            results.append({
                "platform": platform,
                "url": url,
                "text": link.get("text"),
            })

    return results


def _extract_policy_links(links: list[dict]) -> list[dict]:
    results = []

    for link in links:
        url = link.get("href", "")
        text = link.get("text", "")

        combined = f"{url} {text}".lower()

        for policy_type, keywords in POLICY_KEYWORDS.items():

            if any(keyword in combined for keyword in keywords):
                results.append({
                    "type": policy_type,
                    "url": url,
                    "text": text,
                })

                break

    return results


def extract_page(page_data: dict) -> dict:
    """
    Convert raw Playwright page data into structured evidence.
    """

    if not page_data.get("success"):
        return {
            "success": False,
            "error": page_data.get("error"),
        }

    text = page_data.get("text", "")
    links = page_data.get("links", [])

    return {
        "success": True,

        "source": {
            "url": page_data.get("url"),
            "title": page_data.get("title"),
            "status_code": page_data.get("status_code"),
        },

        "emails": _extract_emails(text),

        "phone_numbers": _extract_phones(text),

        "prices": _extract_prices(text),

        "social_links": _extract_social_links(links),

        "policy_links": _extract_policy_links(links),

        "links": links,
    }