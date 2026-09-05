import sqlite3
import re

SCHEMA_FILE = "schema.sql"
DB_FILE = "promocoes.db"

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    sql = f.read()

# Add IF NOT EXISTS to CREATE TABLE and CREATE INDEX statements
sql = re.sub(r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)", "CREATE TABLE IF NOT EXISTS ", sql, flags=re.IGNORECASE)
sql = re.sub(r"CREATE\s+INDEX\s+(?!IF\s+NOT\s+EXISTS)", "CREATE INDEX IF NOT EXISTS ", sql, flags=re.IGNORECASE)

conn = sqlite3.connect(DB_FILE)
try:
    conn.executescript(sql)
    print("schema aplicado com sucesso em", DB_FILE)
finally:
    conn.close()
