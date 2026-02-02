import sqlite3, json, os, sys

root = os.path.dirname(__file__)
db = os.path.join(root, 'nightblade.db')

out = {"db_path": db}
if not os.path.exists(db):
    out["error"] = "db_not_found"
    print(json.dumps(out))
    sys.exit(0)

try:
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    out['tables'] = {}
    for t in tables:
        info = {}
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            info['count'] = cur.fetchone()[0]
        except Exception as e:
            info['count_error'] = str(e)
        try:
            cur.execute(f"SELECT * FROM {t} LIMIT 1")
            row = cur.fetchone()
            if row:
                cols = [c[0] for c in cur.description]
                info['sample'] = dict(zip(cols, row))
            else:
                info['sample'] = None
        except Exception as e:
            info['sample_error'] = str(e)
        out['tables'][t] = info
    conn.close()
    print(json.dumps(out, indent=2, default=str))
except Exception as e:
    out['error'] = str(e)
    print(json.dumps(out))
    sys.exit(1)
