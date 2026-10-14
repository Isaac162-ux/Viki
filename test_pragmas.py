import tempfile
import sqlite3
import sys
sys.path.insert(0, r'C:\Users\isaac\ViKi\src')
from viki.memory import SQLiteMemoryStore

with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

# Create store
store = SQLiteMemoryStore(f.name)
conn = store._conn

# Check pragmas
c = store._conn.cursor()
c.execute('PRAGMA journal_mode')
print('journal_mode:', c.fetchone())
c.execute('PRAGMA synchronous')
print('synchronous:', c.fetchone())
c.execute('PRAGMA page_size')
print('page_size:', c.fetchone())
c.execute('PRAGMA cache_size')
print('cache_size:', c.fetchone())
c.execute('PRAGMA temp_store')
print('temp_store:', c.fetchone())
c.execute('PRAGMA mmap_size')
print('mmap_size:', c.fetchone())
c.execute('PRAGMA page_size')
print('page_size:', c.fetchone())

# Check if there are any other differences
c.execute('PRAGMA compile_options')
opts = [row[0] for row in c.fetchall()]
print('Compile options:', opts)

# Check if FTS5 is enabled
c.execute('PRAGMA compile_options')
opts = [row[0] for row in c.fetchall()]
print('FTS5 enabled:', 'ENABLE_FTS5' in opts)