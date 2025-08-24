import re, time, random
import requests
from lxml import html
import phonenumbers
from urllib.parse import urlparse, urlunparse
from typing import Dict, Any, List, Optional

from src.storage import load_yaml_defaults, get_all_xpaths_for_site
from src.utils import SITES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        return None
    return None

def to_doc(html_text: str):
    try:
        return html.fromstring(html_text)
    except Exception:
        return None

def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def normalize_phone(s: str) -> str:
    s = (s or "").strip()
    try:
        p = phonenumbers.parse(s, "US")
        if phonenumbers.is_valid_number(p):
            return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.NATIONAL)
    except Exception:
        pass
    digits = re.sub(r"\D+", "", s)
    return digits

def canonical_href(h: str) -> str:
    if not h:
        return ""
    try:
        u = urlparse(h.strip())
        # Strip tracking params; keep scheme/host/path
        return urlunparse((u.scheme, u.netloc, u.path, "", "", ""))
    except Exception:
        return h.strip()

def extract_first(doc, xpath: str) -> str:
    try:
        nodes = doc.xpath(xpath)
    except Exception:
        return ""
    if not nodes:
        return ""
    n = nodes[0]
    if isinstance(n, str):
        return norm_ws(n)
    try:
        # element
        t = n.text_content() or ""
        return norm_ws(t)
    except Exception:
        return ""

def extract_anchor(doc, xpath: str) -> Dict[str, str]:
    # Get both anchor text and href from a single XPath (that points to <a> or text under it)
    try:
        nodes = doc.xpath(xpath)
    except Exception:
        return {"anchor": "", "href": ""}
    if not nodes:
        return {"anchor": "", "href": ""}
    n = nodes[0]
    if isinstance(n, str):
        # If xpath selects text node, jump to parent link if possible via second try
        anchor_text = norm_ws(n)
        href = ""
        return {"anchor": anchor_text, "href": href}
    # assume element
    try:
        anchor_text = norm_ws(n.text_content() or "")
    except Exception:
        anchor_text = ""
    try:
        href = canonical_href(n.get("href",""))
    except Exception:
        href = ""
    return {"anchor": anchor_text, "href": href}

def choose_yelp_page_type(doc, yelp_defaults: Dict[str, Any]) -> Dict[str, Any]:
    page_types = yelp_defaults.get("page_types", [])
    for pt in page_types:
        det = pt.get("detect")
        if not det:
            continue
        try:
            found = doc.xpath(det)
            if found:
                return pt
        except Exception:
            continue
    # fallback to first
    return page_types[0] if page_types else {}

def select_xpath_list(site: str, field: str, doc) -> List[Dict[str, Any]]:
    # 1) custom DB overrides
    db_map = get_all_xpaths_for_site(site)  # field -> [{priority,xpath}]
    if field in (db_map or {}):
        return sorted(db_map[field], key=lambda x: x.get("priority", 999999))

    # 2) YAML defaults
    d = load_yaml_defaults() or {}
    if site == "yelp":
        yelp_d = d.get("yelp", {})
        pt = choose_yelp_page_type(doc, yelp_d)
        fields = pt.get("fields", {})
        return fields.get(field, [])
    else:
        site_d = (d.get(site, {}) or {})
        return site_d.get(field, [])

def extract_field(site: str, field: str, doc) -> Dict[str, Any]:
    items = select_xpath_list(site, field, doc)
    if field == "website":
        for it in items:
            res = extract_anchor(doc, it.get("xpath",""))
            if res.get("anchor") or res.get("href"):
                return res
        return {"anchor": "", "href": ""}
    else:
        for it in items:
            val = extract_first(doc, it.get("xpath",""))
            if val:
                return {"value": val}
        return {"value": ""}

def compare(field: str, extracted: Dict[str, Any], ssot: Dict[str, str]) -> bool:
    # naive normalization; can be expanded with fuzzy ratios if needed
    if field == "phone":
        return normalize_phone(extracted.get("value","")) == normalize_phone(ssot.get("phone",""))
    if field == "website":
        return canonical_href(extracted.get("href","")) == canonical_href(ssot.get("website",""))
    if field == "address":
        a = re.sub(r"[,\n]", " ", extracted.get("value","")).lower().strip()
        b = re.sub(r"[,\n]", " ", ssot.get("address","")).lower().strip()
        return re.sub(r"\s+", " ", a) == re.sub(r"\s+", " ", b)
    if field == "name":
        return extracted.get("value","").strip().lower() == (ssot.get("name","").strip().lower())
    if field == "hours":
        A = re.sub(r"\s+", " ", extracted.get("value","").lower().strip())
        B = re.sub(r"\s+", " ", (ssot.get("hours","") or "").lower().strip())
        return (A == B) if (A or B) else False
    return False

def scrape_url(url: str) -> Any:
    html_text = fetch(url)
    if not html_text:
        return None
    return to_doc(html_text)

def scan_client(client: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    # Build SSOT dict
    ssot = {
        "name": client.get("ssot_name",""),
        "address": client.get("ssot_address",""),
        "phone": client.get("ssot_phone",""),
        "website": client.get("ssot_website",""),
        "hours": client.get("ssot_hours",""),
    }
    site_urls = {
        "google": client.get("url_google",""),
        "apple": client.get("url_apple",""),
        "bing": client.get("url_bing",""),
        "yelp": client.get("url_yelp",""),
        "yahoo": client.get("url_yahoo",""),
    }

    out: Dict[str, Dict[str, Any]] = {}
    for site, url in site_urls.items():
        site_data = { "name": {}, "address": {}, "phone": {}, "website": {}, "hours": {} }
        if not url:
            out[site] = site_data
            continue
        time.sleep(random.uniform(0.8, 1.8))  # be polite
        doc = scrape_url(url)
        if doc is None:
            out[site] = site_data
            continue
        for field in ["name","address","phone","website","hours"]:
            extracted = extract_field(site, field, doc)
            site_data[field] = extracted
            try:
                site_data[field]["match"] = compare(field, extracted, ssot)
            except Exception:
                site_data[field]["match"] = False
        out[site] = site_data
    return out

def test_xpath_on_url(url: str, xpath: str, field: str):
    doc = scrape_url(url)
    if doc is None:
        return {"ok": False, "error": "Failed to fetch or parse HTML"}
    if field == "website":
        res = extract_anchor(doc, xpath)
        return {"ok": True, "result": res}
    else:
        val = extract_first(doc, xpath)
        return {"ok": True, "result": {"value": val}}
