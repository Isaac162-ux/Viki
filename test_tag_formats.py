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

# Check what the trigger actually does
c.execute('SELECT sql FROM sqlite_master WHERE type="trigger" AND name="memories_fts_insert"')
result = c.fetchone()
if result:
    print('Trigger SQL:')
    print(result[0])

# Check the actual values being inserted by the trigger
# by examining a sample entry
import json
sample_tags = json.dumps(['style', 'preference'])
print(f'Sample tags JSON: {sample_tags}')

# Test inserting the exact values that the trigger would use
print('Testing trigger values...')
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'User prefers concise answers', '["style", "preference"]', '{}', 'user'))
    print('Trigger simulation OK!')
except Exception as e:
    print(f'Trigger simulation failed: {e}')

# Check if there's an issue with the JSON format
# The tags column in memories is a JSON string, but FTS5 might not like the JSON format
# Let's test with different tag formats
test_tags = [
    '["style", "preference"]',
    'style, preference',
    'style;preference',
    'style preference',
    'style',
    '',
]

for tags in test_formats:
    try:
        c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
                  ('test', 'content', tags, '{}', 'user'))
        print(f'Format "{tags}" OK')
    except Exception as e:
        print(f'Format "{tags}" failed: {e}')