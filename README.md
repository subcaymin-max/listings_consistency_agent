# Listings Consistency Agent (Streamlit + GitHub)

A lightweight Streamlit app that **scrapes 5 listings** (Google Business Profile, Apple Maps, Bing Maps, Yelp, Yahoo Local),
using **XPaths (not schema)** that you control, then compares results to a **Single Source of Truth (SSOT)** for each client.

## Key Features
- **Dashboard** — scan live pages and compare Name, Address, Phone, Website (URL + anchor), and Hours vs SSOT
- **Client Manager** — add/edit clients, SSOT fields, and 5 listing URLs (GBP, Apple, Bing, Yelp, Yahoo)
- **XPath Manager** — manage **multiple XPaths per site/field**, set priority, and **test** XPaths on a sample URL
- **Yelp Smart Types** — define multiple Yelp page types with a **detect XPath**; app picks the right set automatically
- **SQLite storage** (default) — simple persistence for teams; can be swapped to your DB later
- **Requests + lxml** — fast, server-side HTML fetch and XPath extraction (no schema usage)

> ⚠️ **Respect Terms & robots.txt.** These sites change frequently; ship with your own XPaths.
> Some pages are heavily scripted; you may need alternate endpoints or pre-render services.

## Quick Start
1. **Push to GitHub** as a new repo (e.g., `listings_consistency_agent`).
2. Deploy on **Streamlit Community Cloud**.
3. Make sure the app uses **Python 3.11** (see `runtime.txt`) so `lxml` wheels install cleanly.
4. Fill **Client Manager** with a client’s SSOT + listing URLs.
5. Add/adjust XPaths in **XPath Manager**. Use **Test XPath** with a sample URL.
6. Run a **Scan** from the **Dashboard** to see matches/mismatches.

## Project Structure
```
app.py
pages/
  01_📊_Dashboard.py
  02_👤_Client_Manager.py
  03_🧭_XPath_Manager.py
src/
  scraper.py
  storage.py
  utils.py
data/
  default_xpaths.yaml
.streamlit/
  config.toml
requirements.txt
runtime.txt
```

## Pinning Python & Requirements
- `runtime.txt` pins **Python 3.11** (fixes `lxml` build errors on 3.13).
- `requirements.txt` has `lxml`, `requests`, `phonenumbers`, `PyYAML`, `pandas`, `streamlit`.

## Notes
- This app uses **server-side requests** and **simple headers**. For tougher pages, consider adding proxies,
  backoff, cookie jars, or a prerender service.
- Data is stored in `data/app.db` (SQLite). For team-wide persistence across redeploys, wire this to
  **Supabase / Postgres / Google Sheets** later (stubs are easy to add).

