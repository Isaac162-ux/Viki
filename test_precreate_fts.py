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

# Check if memories_fts already exists before the store creates it
# (it shouldn't, since we just created the store)

# Let's trace through the store initialization
print('Store created, checking what tables exist...')
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('Tables after store creation:', [t[0] for t in tables])

# Check if memories_fts exists and its schema
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memories_fts'")
result = c.fetchone()
if result:
    print('memories_fts exists with schema:')
    print(result[0])
else:
    print('memories_fts does not exist yet')

# Try to manually create the FTS table BEFORE the store creates it
print('\\nDropping any existing FTS tables...')
c.execute('DROP TABLE IF EXISTS memories_fts')
c.execute('DROP TABLE IF EXISTS memories_fts_data')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
c.execute('DROP TABLE IF EXISTS memories_fts_content')
c.execute('DROP TABLE IF EXISTS memories_fts_docsize')
c.execute('DROP TABLE IF EXISTS memories_fts_config')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
c.execute('DROP TRIGGER IF EXISTS memories_fts_insert')
c.execute('DROP TRIGGER IF EXISTS memories_fts_delete')
c.execute('DROP TRIGGER IF EXISTS memories_fts_update')
conn.commit()

# Now manually create the FTS table BEFORE the store tries to
c.execute('''
    CREATE VIRTUAL TABLE memories_fts USING fts5(
        content, tags, metadata, source,
        tokenize='porter unicode61'
    )
''')
conn.commit()

print('Pre-created FTS table, now creating store...')

# Now create a NEW store which should use the existing FTS table
store2 = SQLiteMemoryStore(db_path)
conn2 = store2._conn
c2 = conn2.cursor()

# Test insert
try:
    c2.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
               ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('Pre-created FTS insert OK!')
except Exception as e:
    print(f'Pre-created FTS failed: {e}')
    import traceback
    traceback.print_exc()