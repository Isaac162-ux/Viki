import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

c.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content, tags, metadata, source, tokenize='porter unicode61')")
print('FTS5 created')

try:
    c.execute('INSERT INTO test_fts (rowid, content, tags, metadata, source) VALUES (?, ?, ?, ?, ?)',
              ('test-id', 'test content', '[\"style\", \"preference\"]', '{}', 'user'))
    print('Insert OK!')
except Exception as e:
    print(f'Failed: {e}')

# Check table info
c.execute('PRAGMA table_info(test_fts)')
for row in c.fetchall():
    print(f'Col: {row[1]} type={row[2]}')