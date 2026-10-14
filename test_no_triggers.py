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

# Drop the triggers
print('Dropping triggers...')
c.execute('DROP TRIGGER IF EXISTS memories_fts_insert')
c.execute('DROP TRIGGER IF EXISTS memories_fts_delete')
c.execute('DROP TRIGGER IF EXISTS memories_fts_update')

# Drop FTS table
c.execute('DROP TABLE IF EXISTS memories_fts')
c.execute('DROP TABLE IF EXISTS memories_fts_data')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
c.execute('DROP TABLE IF EXISTS memories_fts_content')
c.execute('DROP TABLE IF EXISTS memories_fts_docsize')
c.execute('DROP TABLE IF EXISTS memories_fts_config')
c.execute('DROP TABLE IF EXISTS memories_fts_idx')
conn.commit()

print('Triggers and FTS dropped, testing insert...')
try:
    c.execute('''
        INSERT INTO memories (id, memory_type, content, metadata, created_at, updated_at, accessed_at, access_count, priority, tags, source, confidence, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test-id', 'semantic', 'test', '{}', 1.0, 1.0, 1.0, 0, 50, '[]', 'user', 1.0, None))
    print('SUCCESS without FTS triggers!')
except Exception as e:
    print(f'Failed without FTS: {e}')
    import traceback
    traceback.print_exc()