import streamlit as st
from src.storage import ensure_db, list_clients, upsert_client, get_client_by_id, delete_client
from src.utils import SITES

st.set_page_config(page_title="Client Manager", page_icon="👤", layout="wide")
ensure_db()

st.title("👤 Client Manager")

clients = list_clients()
existing_map = {f"{c['name']} (ID {c['id']})": c['id'] for c in clients}

mode = st.radio("Mode", ["Add", "Edit/Delete"], horizontal=True)

if mode == "Add":
    with st.form("add_client"):
        st.subheader("Basic")
        name = st.text_input("Client Name", placeholder="Acme Clinic")
        ssot_name = st.text_input("SSOT – Entity Name")
        ssot_address = st.text_area("SSOT – Address", height=80)
        ssot_phone = st.text_input("SSOT – Phone")
        ssot_website = st.text_input("SSOT – Website URL")
        ssot_hours = st.text_area("SSOT – Hours (freeform)", height=80)

        st.subheader("Listing URLs")
        url_google = st.text_input("Google Business Profile URL")
        url_apple = st.text_input("Apple Maps URL")
        url_bing = st.text_input("Bing Maps/Places URL")
        url_yelp = st.text_input("Yelp URL")
        url_yahoo = st.text_input("Yahoo Local URL")

        submitted = st.form_submit_button("Save Client", type="primary")
        if submitted:
            cid = upsert_client(None, {
                "name": name.strip(),
                "ssot_name": ssot_name.strip(),
                "ssot_address": ssot_address.strip(),
                "ssot_phone": ssot_phone.strip(),
                "ssot_website": ssot_website.strip(),
                "ssot_hours": ssot_hours.strip(),
                "url_google": url_google.strip(),
                "url_apple": url_apple.strip(),
                "url_bing": url_bing.strip(),
                "url_yelp": url_yelp.strip(),
                "url_yahoo": url_yahoo.strip(),
            })
            st.success(f"Client saved (ID {cid}).")

else:
    if not clients:
        st.info("No clients yet.")
        st.stop()

    choice = st.selectbox("Select Client", list(existing_map.keys()))
    client = get_client_by_id(existing_map[choice])

    with st.form("edit_client"):
        st.subheader("Basic")
        name = st.text_input("Client Name", value=client["name"] or "")
        ssot_name = st.text_input("SSOT – Entity Name", value=client.get("ssot_name",""))
        ssot_address = st.text_area("SSOT – Address", value=client.get("ssot_address",""), height=80)
        ssot_phone = st.text_input("SSOT – Phone", value=client.get("ssot_phone",""))
        ssot_website = st.text_input("SSOT – Website URL", value=client.get("ssot_website",""))
        ssot_hours = st.text_area("SSOT – Hours (freeform)", value=client.get("ssot_hours",""), height=80)

        st.subheader("Listing URLs")
        url_google = st.text_input("Google Business Profile URL", value=client.get("url_google",""))
        url_apple = st.text_input("Apple Maps URL", value=client.get("url_apple",""))
        url_bing = st.text_input("Bing Maps/Places URL", value=client.get("url_bing",""))
        url_yelp = st.text_input("Yelp URL", value=client.get("url_yelp",""))
        url_yahoo = st.text_input("Yahoo Local URL", value=client.get("url_yahoo",""))

        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("Save Changes", type="primary")
        if submitted:
            cid = upsert_client(client["id"], {
                "name": name.strip(),
                "ssot_name": ssot_name.strip(),
                "ssot_address": ssot_address.strip(),
                "ssot_phone": ssot_phone.strip(),
                "ssot_website": ssot_website.strip(),
                "ssot_hours": ssot_hours.strip(),
                "url_google": url_google.strip(),
                "url_apple": url_apple.strip(),
                "url_bing": url_bing.strip(),
                "url_yelp": url_yelp.strip(),
                "url_yahoo": url_yahoo.strip(),
            })
            st.success(f"Client updated (ID {cid}).")

        if col2.form_submit_button("Delete Client", type="secondary"):
            delete_client(client["id"])
            st.success("Client deleted. Refresh to see list updated.")
