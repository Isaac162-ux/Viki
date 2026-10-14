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

# Print triggers
c.execute('SELECT name, sql FROM sqlite_master WHERE type="trigger"')
triggers = c.fetchall()
for t in triggers:
    print(f'Trigger: {t["name"]}')
    print(t['sql'])
    print('---')

# Also check if there are any views or other objects
c.execute('SELECT type, name FROM sqlite_master')
for row in c.fetchall():
    print(f'{row[0]}: {row[1]}')