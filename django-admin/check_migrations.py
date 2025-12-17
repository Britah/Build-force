import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check applied migrations
cursor.execute("SELECT app, name FROM django_migrations WHERE app='labourers' ORDER BY id")
print("Applied migrations:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\nContract table columns:")
cursor.execute("PRAGMA table_info(labourers_contract)")
for row in cursor.fetchall():
    print(f"  {row[1]}")

conn.close()
