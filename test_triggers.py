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

# Test basic insert
print('Testing basic insert...')
try:
    c.execute('INSERT INTO memories (id, memory_type, content, metadata, created_at, updated_at, accessed_at, access_count, priority, tags, source, confidence, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
              ('test-id', 'semantic', 'test', '{}', 1.0, 1.0, 1.0, 0, 50, '[]', 'user', 1.0, None))
    print('SUCCESS with None for expires_at')
except Exception as e:
    print(f'Failed with None: {e}')

# Check for triggers
c.execute('SELECT name, sql FROM sqlite_master WHERE type="trigger"')
triggers = c.fetchall()
print(f'Triggers: {triggers}')

# Check for CHECK constraints
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memories'")
result = c.fetchone()
if result:
    sql = result[0]
    if 'CHECK' in sql.upper():
        print('CHECK constraints found')
    else:
        print('No CHECK constraints')
    
    # Print full schema for inspection
    print('Full schema:')
    print(result[0])