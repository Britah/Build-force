import sqlite3
import os

# Get the path to the database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if generated_content column exists in labourers_contract table
    cursor.execute("PRAGMA table_info(labourers_contract)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'generated_content' not in columns:
        print("Adding generated_content to labourers_contract table...")
        cursor.execute("""
            ALTER TABLE labourers_contract 
            ADD COLUMN generated_content TEXT DEFAULT ''
        """)
        print("✓ Added generated_content to labourers_contract")
    else:
        print("✓ generated_content already exists in labourers_contract")
    
    # Commit the changes
    conn.commit()
    print("\n✓ Database updated successfully!")
    
except sqlite3.Error as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
