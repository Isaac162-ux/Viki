import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Test 1: No tokenizer
c.execute('CREATE VIRTUAL TABLE t1 USING fts5(content, tags)')
try:
    c.execute('INSERT INTO t1 (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('No tokenizer: OK')
except Exception as e:
    print(f'No tokenizer failed: {e}')

# Test 2: porter tokenizer
c.execute('CREATE VIRTUAL TABLE t2 USING fts5(content, tags, tokenize=porter)')
try:
    c.execute('INSERT INTO t2 (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('porter tokenizer: OK')
except Exception as e:
    print(f'porter failed: {e}')

# Test 3: unicode61
c.execute('CREATE VIRTUAL TABLE t3 USING fts5(content, tags, tokenize=unicode61)')
try:
    c.execute('INSERT INTO t3 (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('unicode61: OK')
except Exception as e:
    print(f'unicode61 failed: {e}')

# Test 4: porter unicode61
c.execute("CREATE VIRTUAL TABLE t4 USING fts5(content, tags, tokenize='porter unicode61')")
try:
    c.execute('INSERT INTO t4 (content, tags) VALUES (?, ?)', ('test', 'tag1'))
    print('porter unicode61: OK')
except Exception as e:
    print(f'porter unicode61 failed: {e}')