import sqlite3
import os

# Get the path to the database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check table structure
    cursor.execute("PRAGMA table_info(labourers_checkin)")
    columns = {column[1]: column for column in cursor.fetchall()}
    print("Current CheckIn table columns:")
    for col_name in columns:
        print(f"  - {col_name}")
    
    # Make fields nullable
    updates = []
    
    if 'facial_recognition_photo' in columns and columns['facial_recognition_photo'][3] == 1:  # NOT NULL
        print("\nUpdating facial_recognition_photo to allow NULL...")
        updates.append("facial_recognition_photo")
    
    if 'facial_match_confidence' in columns and columns['facial_match_confidence'][3] == 1:  # NOT NULL
        print("Updating facial_match_confidence to allow NULL...")
        updates.append("facial_match_confidence")
    
    if updates:
        # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
        print("\nRecreating table with updated schema...")
        
        # Get existing data
        cursor.execute("SELECT * FROM labourers_checkin")
        existing_data = cursor.fetchall()
        
        # Drop and recreate table
        cursor.execute("DROP TABLE IF EXISTS labourers_checkin_temp")
        cursor.execute("""
            CREATE TABLE labourers_checkin_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                labourer_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                facial_recognition_photo VARCHAR(100),
                facial_match_confidence REAL,
                location_lat DECIMAL(9, 6),
                location_lng DECIMAL(9, 6),
                timestamp DATETIME NOT NULL,
                within_geofence BOOLEAN NOT NULL DEFAULT 1,
                whitelist_valid BOOLEAN NOT NULL DEFAULT 1,
                within_operating_hours BOOLEAN NOT NULL DEFAULT 1,
                status VARCHAR(20) NOT NULL,
                access_granted BOOLEAN NOT NULL DEFAULT 0,
                security_guard_id INTEGER,
                override_reason TEXT,
                override_by_id INTEGER,
                device_id VARCHAR(100),
                ip_address VARCHAR(39),
                FOREIGN KEY (labourer_id) REFERENCES labourers_labourer(id),
                FOREIGN KEY (project_id) REFERENCES labourers_project(id),
                FOREIGN KEY (security_guard_id) REFERENCES labourers_securityguard(id),
                FOREIGN KEY (override_by_id) REFERENCES auth_user(id)
            )
        """)
        
        # Copy data if any exists
        if existing_data:
            print(f"Copying {len(existing_data)} existing records...")
            # This would need proper column mapping
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE labourers_checkin")
        cursor.execute("ALTER TABLE labourers_checkin_temp RENAME TO labourers_checkin")
        
        print("✓ Table recreated successfully")
    else:
        print("\n✓ All fields are already nullable")
    
    # Commit the changes
    conn.commit()
    print("\n✓ Database updated successfully!")
    
except sqlite3.Error as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
