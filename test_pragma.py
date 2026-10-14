import tempfile
import sqlite3
import sys
sys.path.insert(0, r'C:\Users\isaac\ViKi\src')
from viki.memory import SQLiteMemoryStore

with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

store = SQLiteMemoryStore(f.name)
conn = store._conn
c = conn.cursor()

print('PRAGMA strict:')
c.execute('PRAGMA strict')
print(c.fetchall())

print('SQLite compile options:')
c.execute('PRAGMA compile_options')
for row in c.fetchall():
    print(f'  {row[0]}')

print('SQLite version:', sqlite3.sqlite_version)

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memories'")
result = c.fetchone()
if result:
    sql = result[0]
    print('Table SQL contains STRICT:', 'STRICT' in sql.upper())
    print('Full SQL:')
    print(result[0])