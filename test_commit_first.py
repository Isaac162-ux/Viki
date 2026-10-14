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

# Check if the FTS table creation is in a transaction
print('Isolation level:', conn.isolation_level)
print('In transaction:', conn.in_transaction)

# Try committing before creating FTS table
conn.commit()
print('Committed, now creating FTS table...')

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

c.execute('''
    CREATE VIRTUAL TABLE memories_fts USING fts5(
        content, tags, metadata, source,
        tokenize='porter unicode61'
    )
''')
conn.commit()

print('FTS table created and committed, testing insert...')
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('Insert after commit OK!')
except Exception as e:
    print(f'Failed after commit: {e}')
    import traceback
    traceback.print_exc()