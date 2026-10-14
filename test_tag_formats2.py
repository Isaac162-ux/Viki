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

# Test different tag formats
test_formats = [
    '["style", "preference"]',
    'style, preference',
    'style;preference',
    'style preference',
    'style',
    '',
    'tag1 tag2',
    'tag1,tag2',
]

for tags in test_formats:
    try:
        c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
                  ('test', 'content', tags, '{}', 'user'))
        print(f'Format "{tags}" OK')
    except Exception as e:
        print(f'Format "{tags}" failed: {e}')

# Also test with no tags column (NULL)
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test', 'content', None, '{}', 'user'))
    print('NULL tags OK')
except Exception as e:
    print(f'NULL tags failed: {e}')

# Test with empty string
try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test', 'content', '', '{}', 'user'))
    print('Empty string tags OK')
except Exception as e:
    print(f'Empty string failed: {e}')