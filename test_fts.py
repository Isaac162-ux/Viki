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

# Check FTS table schema
c.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="memories_fts"')
result = c.fetchone()
if result:
    print('FTS table schema:')
    print(result[0])

# Check FTS table columns
c.execute('PRAGMA table_info(memories_fts)')
for row in c.fetchall():
    print(f'FTS column: {row[1]}: {row[2]}')

# Check triggers again
c.execute('SELECT name, sql FROM sqlite_master WHERE type="trigger" AND tbl_name="memories"')
triggers = c.fetchall()
for t in triggers:
    print(f'Trigger: {t[0]}')
    print(t[1])
    print('---')