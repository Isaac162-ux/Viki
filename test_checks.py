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

print('Checking triggers...')
c.execute('SELECT name, sql FROM sqlite_master WHERE type="trigger" AND tbl_name="memories"')
triggers = c.fetchall()
for t in c.fetchall():
    print('Trigger:', t[0])
    print(t[1])
    print('---')

# Check for any CHECK constraints
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memories'")
result = c.fetchone()
if result:
    sql = result[0]
    if 'CHECK' in sql.upper():
        print('CHECK constraints found')
    else:
        print('No CHECK constraints')
    
    # Check for STRICT
    if 'STRICT' in sql.upper():
        print('STRICT table!')
    else:
        print('Not STRICT')