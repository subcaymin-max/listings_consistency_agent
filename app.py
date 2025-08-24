import streamlit as st
import pandas as pd
from src.storage import ensure_db
from src.utils import SITES

st.set_page_config(page_title="Listings Consistency Agent", page_icon="🧭", layout="wide")
ensure_db()

st.title("Listings Consistency Agent")
st.write("Use the sidebar to navigate: **Dashboard**, **Client Manager**, **XPath Manager**.")

st.markdown(
    """
- **Dashboard** scans live pages and compares to your SSOT.
- **Client Manager** adds/edits clients, their SSOT, and 5 listing URLs.
- **XPath Manager** manages multiple XPaths per site/field and lets you **test** them.
    """
)

st.divider()
st.subheader("Quick Links")
cols = st.columns(3)
with cols[0]:
    st.page_link("pages/01_📊_Dashboard.py", label="📊 Go to Dashboard")
with cols[1]:
    st.page_link("pages/02_👤_Client_Manager.py", label="👤 Go to Client Manager")
with cols[2]:
    st.page_link("pages/03_🧭_XPath_Manager.py", label="🧭 Go to XPath Manager")

st.divider()
st.caption("Respect each site's Terms and robots.txt. XPaths here are user-configurable and may require updates as sites evolve.")
