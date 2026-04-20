import sqlite3

conn = sqlite3.connect('jewelry.db')
cursor = conn.cursor()

# Add delivery_charge column to orders table if not exists
try:
    cursor.execute('ALTER TABLE orders ADD COLUMN delivery_charge REAL DEFAULT 0')
    print("✅ Added delivery_charge column to orders table")
except sqlite3.OperationalError:
    print("⚠️ delivery_charge column already exists")

# Add subtotal column to orders table if not exists
try:
    cursor.execute('ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0')
    print("✅ Added subtotal column to orders table")
except sqlite3.OperationalError:
    print("⚠️ subtotal column already exists")

# Create notifications table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        name TEXT,
        email TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ Notifications table created")

conn.commit()
conn.close()
print("\n✅ Database migration completed successfully!")