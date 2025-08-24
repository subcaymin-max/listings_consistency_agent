import streamlit as st
import pandas as pd
from src.storage import ensure_db, list_xpaths, add_xpath, delete_xpath, load_yaml_defaults, get_all_xpaths_for_site
from src.scraper import test_xpath_on_url
from src.utils import SITES, FIELDS

st.set_page_config(page_title="XPath Manager", page_icon="🧭", layout="wide")
ensure_db()

st.title("🧭 XPath Manager")

st.markdown("""
Manage **multiple XPaths per site & field**. Higher **priority** runs first.
Use **Test XPath** to validate against a real URL before saving.
""")

site = st.selectbox("Site", SITES)
field = st.selectbox("Field", FIELDS)

st.subheader("Existing XPaths")
xlist = list_xpaths(site, field)
if xlist:
    df = pd.DataFrame(xlist)
    df = df.sort_values(by="priority").reset_index(drop=True)
    st.dataframe(df[["id","site","field","priority","xpath"]], use_container_width=True, hide_index=True)
    to_delete = st.multiselect("Select IDs to delete", df["id"].tolist())
    if st.button("Delete Selected"):
        for xid in to_delete:
            delete_xpath(xid)
        st.success("Deleted. Refresh to see updates.")
else:
    st.info("No custom XPaths yet. Defaults from YAML will be used.")

st.divider()

st.subheader("Add New XPath")
with st.form("add_xpath_form"):
    xpath = st.text_input("XPath", placeholder="//h1//text() or //a[contains(.,'Website')]")
    priority = st.number_input("Priority (lower runs first)", min_value=1, value=1, step=1)
    sample_url = st.text_input("Sample URL for Test", placeholder="https://...")
    col1, col2 = st.columns(2)
    tested = col1.form_submit_button("Test XPath")
    saved = col2.form_submit_button("Save XPath", type="primary")

    if tested and sample_url.strip() and xpath.strip():
        with st.spinner("Testing..."):
            res = test_xpath_on_url(sample_url.strip(), xpath.strip(), field)
        st.write("**Result**")
        st.json(res)

    if saved and xpath.strip():
        add_xpath(site, field, priority, xpath.strip())
        st.success("XPath saved. Refresh to see it listed above.")

st.divider()
st.subheader("YAML Defaults (read-only)")
defaults = load_yaml_defaults()
st.code(str(defaults.get(site, {}))[:2000])
