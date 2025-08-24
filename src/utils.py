SITES = ["google", "apple", "bing", "yelp", "yahoo"]
FIELDS = ["name", "address", "phone", "website", "hours"]

def canonicalize_site_key(url: str) -> str:
    url = (url or "").lower()
    if "yelp." in url:
        return "yelp"
    if "google." in url:
        return "google"
    if "apple." in url:
        return "apple"
    if "bing." in url:
        return "bing"
    if "yahoo." in url:
        return "yahoo"
    return ""
