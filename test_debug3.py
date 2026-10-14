import tempfile
import sqlite3
import sys
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

params = store._entry_to_params(entry)

# Connect to the SAME database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Test each column individually
cols = list(params.keys())
vals = list(params.values())

print("Testing each column individually...")
for col, val in zip(cols, vals):
    try:
        c.execute(f"INSERT INTO memories ({col}) VALUES (?)", (val,))
        # Clean up
        c.execute(f"DELETE FROM memories WHERE {col} = ?", (val,))
    except Exception as e:
        print(f"FAILED: {col} = {repr(val)[:50]} (type={type(val).__name__}) -> {e}")

c.close()