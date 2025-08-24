import os, sqlite3, json, yaml
from typing import List, Dict, Any

DB_PATH = os.path.join("data", "app.db")
DEFAULTS_YAML = os.path.join("data", "default_xpaths.yaml")

def ensure_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                ssot_name TEXT,
                ssot_address TEXT,
                ssot_phone TEXT,
                ssot_website TEXT,
                ssot_hours TEXT,
                url_google TEXT,
                url_apple TEXT,
                url_bing TEXT,
                url_yelp TEXT,
                url_yahoo TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS xpaths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT,
                field TEXT,
                priority INTEGER,
                xpath TEXT
            )
            """
        )
        con.commit()

def list_clients() -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM clients ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def get_client_by_id(cid: int) -> Dict[str, Any]:
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        row = con.execute("SELECT * FROM clients WHERE id=?", (cid,)).fetchone()
        return dict(row) if row else {}

def upsert_client(cid, data: Dict[str, Any]) -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        if cid:
            cols = ",".join([f"{k}=?" for k in data.keys()])
            cur.execute(f"UPDATE clients SET {cols} WHERE id=?", [*data.values(), cid])
            con.commit()
            return cid
        else:
            keys = ",".join(data.keys())
            qs = ",".join(["?"]*len(data))
            cur.execute(f"INSERT INTO clients ({keys}) VALUES ({qs})", list(data.values()))
            con.commit()
            return cur.lastrowid

def delete_client(cid: int):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM clients WHERE id=?", (cid,))
        con.commit()

def list_xpaths(site: str, field: str):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM xpaths WHERE site=? AND field=?", (site, field)).fetchall()
        return [dict(r) for r in rows]

def get_all_xpaths_for_site(site: str):
    # returns dict[field] -> list of {priority, xpath}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM xpaths WHERE site=? ORDER BY priority ASC", (site,)).fetchall()
        data = {}
        for r in rows:
            data.setdefault(r["field"], []).append({"priority": r["priority"], "xpath": r["xpath"]})
        return data

def add_xpath(site: str, field: str, priority: int, xpath: str):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT INTO xpaths (site, field, priority, xpath) VALUES (?,?,?,?)", (site, field, priority, xpath))
        con.commit()

def delete_xpath(xid: int):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM xpaths WHERE id=?", (xid,))
        con.commit()

def load_yaml_defaults():
    if not os.path.exists(DEFAULTS_YAML):
        return {}
    with open(DEFAULTS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
