import streamlit as st
import pandas as pd
from src.storage import ensure_db, list_clients, get_client_by_id, get_all_xpaths_for_site, load_yaml_defaults
from src.scraper import scan_client
from src.utils import SITES, FIELDS

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
ensure_db()

st.title("📊 Dashboard")

clients = list_clients()
if not clients:
    st.info("No clients yet. Add one in **Client Manager**.")
    st.stop()

client_names = {f"{c['name']} (ID {c['id']})": c['id'] for c in clients}
choice = st.selectbox("Choose a client", list(client_names.keys()))
client_id = client_names[choice]
client = get_client_by_id(client_id)

st.subheader("Single Source of Truth (SSOT)")
ssot_cols = st.columns(5)
ssot_cols[0].metric("Name", client.get("ssot_name","") or "—")
ssot_cols[1].metric("Address", client.get("ssot_address","") or "—")
ssot_cols[2].metric("Phone", client.get("ssot_phone","") or "—")
ssot_cols[3].metric("Website", client.get("ssot_website","") or "—")
ssot_cols[4].metric("Hours", client.get("ssot_hours","") or "—")

st.divider()

if st.button("🔍 Scan Now", type="primary"):
    with st.spinner("Scanning..."):
        result = scan_client(client)
        # result = {site: {field: {"value": str, "url": str?, "match": bool}}}
        rows = []
        for site, data in result.items():
            row = {"Site": site}
            for field in FIELDS:
                if field == "website":
                    val = data.get(field, {})
                    label = val.get("anchor","")
                    href = val.get("href","")
                    cell = f"[{label}]({href})" if href else (label or "—")
                    match = "✅" if val.get("match") else "❌"
                else:
                    val = data.get(field, {})
                    cell = val.get("value","") or "—"
                    match = "✅" if val.get("match") else "❌"
                row[f"{field.title()}"] = cell
                row[f"{field.title()} Match"] = match
            rows.append(row)
        df = pd.DataFrame(rows).set_index("Site")
        st.dataframe(df, use_container_width=True)
else:
    st.info("Click **Scan Now** to fetch live data and compare to SSOT.")
