from tools.registry import get_tool


fetch_page = get_tool("fetch_page")
extract_page = get_tool("extract_page")


page = fetch_page(
    url="https://www.nvidia.com/en-us/"
)


if not page.get("success"):
    print("Page fetch failed:")
    print(page)
    raise SystemExit


result = extract_page(page)


print("\n==============================")
print("EXTRACTOR RESULT")
print("==============================")


print("\nSource:")
print(result["source"])


print("\nEmails:")
print(result["emails"])


print("\nPhone numbers:")
print(result["phone_numbers"])


print("\nPrices:")
print(result["prices"])


print("\nSocial links:")
for item in result["social_links"]:
    print(item)


print("\nPolicy links:")
for item in result["policy_links"]:
    print(item)