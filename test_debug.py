import tempfile
import sqlite3
import sys
import traceback
sys.path.insert(0, r'C:\Users\isaac\ViKi\src')
from viki.memory import SQLiteMemoryStore, SemanticMemoryEntry

with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

store = SQLiteMemoryStore(db_path)

entry = SemanticMemoryEntry(
    content='User prefers concise answers',
    category='preference',
    provenance='user_stated',
    tags={'preference', 'style'},
    source='user',
    confidence=0.9
)

# Get params
params = store._entry_to_params(entry)
print("Params:")
for k, v in params.items():
    if v is not None:
        print(f'  {k}: {type(v).__name__} = {repr(v)[:50]}')

# Try direct insert with debug
conn = sqlite3.connect(r'C:\Users\isaac\ViKi\test.db')
c = conn.cursor()

# Get the exact SQL
columns = ", ".join(params.keys())
placeholders = ", ".join([f":{k}" for k in params.keys()])
sql = f"INSERT INTO memories ({', '.join(params.keys())}) VALUES ({', '.join([':'+k for k in params.keys()])})"
print(f"SQL: {sql[:200]}...")

try:
    c.execute(sql, params)
    print("Direct insert OK")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    
    # Try inserting column by column to find the problematic one
    print("\nTrying column by column...")
    cols = list(params.keys())
    vals = list(params.values())
    
    # Try inserting with explicit column list
    try:
        placeholders = ", ".join(["?"] * len(vals))
        c.execute(f"INSERT INTO memories ({', '.join(cols)}) VALUES ({', '.join(['?']*len(vals))})", vals)
        print("Positional insert OK")
    except Exception as e2:
        print(f"Positional error: {e2}")
        
        # Try one by one
        for i, (col, val) in enumerate(zip(cols, vals)):
            try:
                c.execute(f"INSERT INTO memories ({col}) VALUES (?)", (val,))
            except Exception as e3:
                print(f"Column {col} (type={type(val).__name__}, val={repr(val)[:50]}) failed: {e3}")

c.close()