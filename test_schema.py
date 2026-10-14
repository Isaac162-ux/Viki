import tempfile
import sqlite3
import sys
sys.path.insert(0, r'C:\Users\isaac\ViKi\src')
from viki.memory import SQLiteMemoryStore, SemanticMemoryEntry

with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

store = SQLiteMemoryStore(db_path)
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('PRAGMA table_info(memories)')
for row in c.fetchall():
    print(f'{row[1]}: {row[2]} (notnull={row[3]}, pk={row[5]})')

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memories'")
result = c.fetchone()
if result:
    print(result[0])