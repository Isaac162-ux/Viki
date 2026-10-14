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

# Check what the FTS table expects
c.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="memories_fts"')
result = c.fetchone()
if result:
    print('FTS schema:', result[0])

# Check FTS column types
c.execute('PRAGMA table_info(memories_fts)')
for row in c.fetchall():
    print(f'FTS col: {row[1]} type={row[2]}')

# Test inserting directly into FTS table
print('Testing direct FTS insert...')
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '["tag1", "tag2"]', '{}', 'user'))
    print('Direct FTS insert OK!')
except Exception as e:
    print(f'Direct FTS insert failed: {e}')

# Test with the actual trigger values
print('Testing trigger insert simulation...')
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '["style", "preference"]', '{}', 'user'))
    print('FTS insert with JSON tags OK!')
except Exception as e:
    print(f'FTS insert with JSON tags failed: {e}')

# Test with simple tags
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id2', 'test content', 'simple tag', '{}', 'user'))
    print('FTS insert with simple tag OK!')
except Exception as e:
    print(f'FTS insert with simple tag failed: {e}')