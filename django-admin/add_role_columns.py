import sqlite3
import os

# Connect to database
db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of columns to add
columns = [
    "ALTER TABLE labourers_role ADD COLUMN role_type VARCHAR(20) DEFAULT 'CUSTOM'",
    "ALTER TABLE labourers_role ADD COLUMN minimum_experience_years INTEGER DEFAULT 0",
    "ALTER TABLE labourers_role ADD COLUMN requires_certification BOOLEAN DEFAULT 0",
    "ALTER TABLE labourers_role ADD COLUMN requires_background_check BOOLEAN DEFAULT 0",
    "ALTER TABLE labourers_role ADD COLUMN is_active BOOLEAN DEFAULT 1",
    "ALTER TABLE labourers_role ADD COLUMN created_at TIMESTAMP"
]

for sql in columns:
    try:
        cursor.execute(sql)
        print(f"✓ Executed: {sql[:50]}...")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print(f"⚠ Column already exists: {sql[:50]}...")
        else:
            print(f"✗ Error: {e}")

conn.commit()
conn.close()
print("\n✓ Database updated successfully!")
