import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'deepcrop.db')

def get_connection():
    """Establish and return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the database and create tables if they do not exist.
    This fulfills the 'Storage Cylinder' aspect of the architecture diagram.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create satellite_scans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satellite_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            scan_date TIMESTAMP NOT NULL,
            avg_ndvi REAL,
            predicted_crop TEXT,
            confidence REAL,
            dataset_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[INFO] Database initialized at {DB_PATH}")

def insert_scan_record(location_name, lat, lon, avg_ndvi, predicted_crop, confidence, dataset_path=None):
    """Insert a new satellite scan record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    scan_date = datetime.datetime.now()
    
    cursor.execute('''
        INSERT INTO satellite_scans (location_name, latitude, longitude, scan_date, avg_ndvi, predicted_crop, confidence, dataset_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (location_name, lat, lon, scan_date, avg_ndvi, predicted_crop, confidence, dataset_path))
    
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"[INFO] Inserted scan record ID: {scan_id} for {location_name}")
    return scan_id

def get_recent_scans(limit=10):
    """Retrieve the most recent satellite scans."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, location_name, scan_date, avg_ndvi, predicted_crop, confidence, dataset_path
        FROM satellite_scans
        ORDER BY scan_date DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "location_name": row[1],
            "scan_date": row[2],
            "avg_ndvi": row[3],
            "predicted_crop": row[4],
            "confidence": row[5],
            "dataset_path": row[6]
        }
        for row in rows
    ]

if __name__ == '__main__':
    # Initialize the database when script is run directly
    init_db()
