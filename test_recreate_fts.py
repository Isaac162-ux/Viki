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

# Drop and recreate FTS table
print('Dropping FTS table...')
c.execute('DROP TABLE IF EXISTS memories_fts')
c.execute('DROP TABLE IF EXISTS memories_fts_data')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
c.execute('DROP TABLE IF EXISTS memories_fts_content')
c.execute('DROP TABLE IF EXISTS memories_fts_docsize')
c.execute('DROP TABLE IF EXISTS memories_fts_config')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
conn.commit()

# Recreate FTS table manually
print('Recreating FTS table...')
c.execute("""
    CREATE VIRTUAL TABLE memories_fts USING fts5(
        content, tags, metadata, source, 
        tokenize='porter unicode61'
    )
""")
conn.commit()

print('Testing insert...')
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '["style", "preference"]', '{}', 'user'))
    print('Recreated FTS insert OK!')
except Exception as e:
    print(f'Recreated FTS failed: {e}')
    import traceback
    traceback.print_exc()