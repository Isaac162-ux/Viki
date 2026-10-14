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

# Try direct insert with debug using the SAME connection
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get the exact SQL
cols = list(params.keys())
vals = list(params.values())

# Try inserting with explicit column list
placeholders = ", ".join(["?"] * len(vals))
sql = f"INSERT INTO memories ({', '.join(params.keys())}) VALUES ({', '.join(['?']*len(vals))})"
print(f"SQL: {sql[:200]}...")

try:
    c.execute(sql, list(params.values()))
    print("Direct insert OK")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    
    # Try inserting with explicit column list matching table
    print("\nTrying with explicit columns from schema...")
    # Get table schema
    c.execute("PRAGMA table_info(memories)")
    schema_cols = [row[1] for row in c.fetchall()]
    print(f"Schema columns ({len(schema_cols)}): {schema_cols}")
    print(f"Param keys ({len(params)}): {list(params.keys())}")
    
    # Check for mismatch
    param_keys = set(params.keys())
    schema_cols_set = set(schema_cols)
    print(f"Missing in params: {schema_cols_set - param_keys}")
    print(f"Extra in params: {param_keys - schema_cols_set}")
    
    # Try with only schema columns
    filtered_params = {k: v for k, v in params.items() if k in schema_cols}
    print(f"Filtered params: {len(filtered_params)}")
    try:
        cols = list(filtered_params.keys())
        vals = list(filtered_params.values())
        placeholders = ", ".join(["?"] * len(vals))
        sql = f"INSERT INTO memories ({', '.join(cols)}) VALUES ({', '.join(['?']*len(vals))})"
        c.execute(sql, vals)
        print("Filtered insert OK")
    except Exception as e2:
        print(f"Filtered error: {e2}")
        traceback.print_exc()

c.close()