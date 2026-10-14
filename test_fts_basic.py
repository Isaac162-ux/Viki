import sqlite3

# Test with in-memory database
conn = sqlite3.connect(':memory:')
c = conn.cursor()

c.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content, tags, metadata, source, tokenize='porter unicode61')")
print('In-memory FTS5 created')

try:
    c.execute('INSERT INTO test_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('In-memory FTS5 OK!')
except Exception as e:
    print(f'In-memory failed: {e}')

# Test with file database
conn2 = sqlite3.connect('test_fts_file.db')
c2 = conn2.cursor()
c2.execute("CREATE VIRTUAL TABLE test_fts2 USING fts5(content, tags, metadata, source, tokenize='porter unicode61')")
print('File-based FTS5 created')

try:
    c2.execute('INSERT INTO test_fts2 (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
               ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('File-based FTS5 OK!')
except Exception as e:
    print(f'File-based failed: {e}')

# Test with explicit column names
try:
    conn2.execute('INSERT INTO test_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
                  ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('Explicit columns OK!')
except Exception as e:
    print(f'Explicit columns failed: {e}')