import tempfile
import sqlite3
import sys
sys.path.insert(0, r'C:\Users\isaac\ViKi\src')
from viki.memory import SQLiteMemoryStore

with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

store = SQLiteMemoryStore(f.name)
conn = store._conn

print('isolation_level:', store._conn.isolation_level)
print('in_transaction:', store._conn.in_transaction)

# Try setting isolation_level
store._conn.isolation_level = None
print('Set isolation_level to None')

c = store._conn.cursor()
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('After setting isolation_level=None: OK!')
except Exception as e:
    print(f'Still failed: {e}')