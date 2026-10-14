import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Create minimal FTS5 table
c.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content, tags)")
print('Minimal FTS5 created')

# Test insert
try:
    c.execute('INSERT INTO test_fts (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('Minimal FTS5 insert OK!')
except Exception as e:
    print(f'Minimal FTS5 failed: {e}')

# Test with porter unicode61 tokenizer
c.execute("CREATE VIRTUAL TABLE test_fts2 USING fts5(content, tags, tokenize='porter unicode61')")
print('FTS5 with porter unicode61 created')

try:
    c.execute('INSERT INTO test_fts2 (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('FTS5 with tokenizer OK!')
except Exception as e:
    print(f'FTS5 with tokenizer failed: {e}')

# Test with JSON tags
try:
    c.execute('INSERT INTO test_fts2 (content, tags) VALUES (?, ?)', ('test', '[\"tag1\", \"tag2\"]'))
    print('JSON tags OK!')
except Exception as e:
    print(f'JSON tags failed: {e}')

# Test with the exact tokenizer from the schema
c.execute("CREATE VIRTUAL TABLE test_fts3 USING fts5(content, tags, metadata, source, tokenize='porter unicode61')")
print('Full FTS5 schema created')

try:
    c.execute('INSERT INTO test_fts3 (content, tags, metadata, source) VALUES (?, ?, ?, ?)', 
              ('test content', '[\"tag1\", \"tag2\"]', '{}', 'user'))
    print('Full schema insert OK!')
except Exception as e:
    print(f'Full schema insert failed: {e}')