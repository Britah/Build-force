import sqlite3
import os

# Get the path to the database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if created_by column exists in labourers_contract table
    cursor.execute("PRAGMA table_info(labourers_contract)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'created_by_id' not in columns:
        print("Adding created_by_id to labourers_contract table...")
        cursor.execute("""
            ALTER TABLE labourers_contract 
            ADD COLUMN created_by_id INTEGER NULL 
            REFERENCES auth_user(id)
        """)
        print("✓ Added created_by_id to labourers_contract")
    else:
        print("✓ created_by_id already exists in labourers_contract")
    
    # Check if created_by column exists in labourers_contracttemplate table
    cursor.execute("PRAGMA table_info(labourers_contracttemplate)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'created_by_id' not in columns:
        print("Adding created_by_id to labourers_contracttemplate table...")
        cursor.execute("""
            ALTER TABLE labourers_contracttemplate 
            ADD COLUMN created_by_id INTEGER NULL 
            REFERENCES auth_user(id)
        """)
        print("✓ Added created_by_id to labourers_contracttemplate")
    else:
        print("✓ created_by_id already exists in labourers_contracttemplate")
    
    # Commit the changes
    conn.commit()
    print("\n✓ Database updated successfully!")
    
except sqlite3.Error as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
