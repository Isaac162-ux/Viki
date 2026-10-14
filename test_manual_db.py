import sqlite3
import os

db_path = 'test_manual.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect('test_manual.db')
c = conn.cursor()

c.execute('''
    CREATE VIRTUAL TABLE memories_fts USING fts5(
        content, tags, metadata, source,
        tokenize='porter unicode61'
    )
''')
print('Manual FTS5 created')

try:
    c.execute('INSERT INTO memories_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('Manual DB insert OK!')
except Exception as e:
    print(f'Manual DB failed: {e}')
    import traceback
    traceback.print_exc()