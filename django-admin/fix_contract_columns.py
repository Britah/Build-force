import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("Adding missing columns to labourers_contract table...")

# List of columns to add based on migration 0004
columns_to_add = [
    ("acknowledgment_ip", "char(39) NULL"),
    ("acknowledgment_method", "varchar(50) NOT NULL DEFAULT ''"),
    ("audit_log", "text NOT NULL DEFAULT '[]'"),
    ("created_at", "datetime NULL"),
    ("delivery_status", "varchar(50) NOT NULL DEFAULT ''"),
    ("generated_pdf", "varchar(100) NULL"),
    ("sent_to", "varchar(200) NOT NULL DEFAULT ''"),
    ("signature_data", "text NOT NULL DEFAULT ''"),
    ("signature_device", "varchar(200) NOT NULL DEFAULT ''"),
    ("signature_verified", "integer NOT NULL DEFAULT 0"),
    ("updated_at", "datetime NULL"),
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE labourers_contract ADD COLUMN {col_name} {col_type}")
        print(f"  ✓ Added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"  - Column already exists: {col_name}")
        else:
            print(f"  ✗ Error adding {col_name}: {e}")

conn.commit()
print("\nVerifying columns...")
cursor.execute("PRAGMA table_info(labourers_contract)")
print(f"Total columns: {len(cursor.fetchall())}")

conn.close()
print("\nDone!")
