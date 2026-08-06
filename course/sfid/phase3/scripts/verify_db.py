import sqlite3
import os

db_path = "../phase3/output/b1_vocab.db"

if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
    print("[ERROR] Database file does not exist or is empty.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Count rows
cursor.execute("SELECT COUNT(*) FROM b1_vocabulary")
row_count = cursor.fetchone()[0]

if row_count != 3307:
    print(f"[ERROR] Row count mismatch. Expected 3307, got {row_count}.")
else:
    print(f"[SUCCESS] Row count matches perfectly: {row_count}")

# 2. Check for NULLs or empty strings
cursor.execute('''
    SELECT COUNT(*) FROM b1_vocabulary 
    WHERE en_translation IS NULL OR en_translation = ''
       OR sv_context IS NULL OR sv_context = ''
       OR source IS NULL OR source = ''
''')
null_count = cursor.fetchone()[0]

if null_count > 0:
    print(f"[ERROR] Found {null_count} rows with NULL or empty string values.")
else:
    print(f"[SUCCESS] Zero NULL or empty string values found in the database.")

conn.close()

# Generate Report
report = f"""# Phase 3 Database Validation Report

## Checks Performed
- **Total Rows**: {row_count} / 3307 (100% Coverage of Found Words)
- **Null Values**: {null_count}
- **Status**: {"PASSED" if row_count == 3307 and null_count == 0 else "FAILED"}
"""
os.makedirs("../phase3/reports", exist_ok=True)
with open("../phase3/reports/phase3_validation.md", "w") as f:
    f.write(report)
    
print("Validation report saved to reports/phase3_validation.md")
