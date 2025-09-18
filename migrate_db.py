#!/usr/bin/env python3
"""
Database migration script to add ML fields to Photo table.
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add alt_text and detected_objects columns to the photo table."""
    db_path = Path(__file__).parent / 'data-dev.db'
    
    if not db_path.exists():
        print("Database not found. Please run the app first to create the database.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(photo)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'alt_text' not in columns:
            cursor.execute("ALTER TABLE photo ADD COLUMN alt_text VARCHAR(500)")
            print("Added alt_text column")
        else:
            print("alt_text column already exists")
            
        if 'detected_objects' not in columns:
            cursor.execute("ALTER TABLE photo ADD COLUMN detected_objects TEXT")
            print("Added detected_objects column")
        else:
            print("detected_objects column already exists")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()