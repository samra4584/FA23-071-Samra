import sqlite3
import os

def migrate_database():
    """Add all new tables for reviews, product images, and temp users"""
    
    conn = sqlite3.connect('jewelry.db')
    cursor = conn.cursor()
    
    print("=" * 50)
    print("DATABASE MIGRATION - Elite Sparkle")
    print("=" * 50)
    
    # 1. Create product_images table for multiple product images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    ''')
    print("✅ Table 'product_images' created")
    
    # 2. Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            title TEXT,
            comment TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("✅ Table 'reviews' created")
    
    # 3. Create temp_users table for registration OTP verification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            otp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (datetime('now', '+10 minutes'))
        )
    ''')
    print("✅ Table 'temp_users' created")
    
    # 4. Add review_sent column to orders table if not exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'review_sent' not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN review_sent INTEGER DEFAULT 0")
        print("✅ Column 'review_sent' added to orders table")
    else:
        print("✅ Column 'review_sent' already exists")
    
    # 5. Migrate existing product images to product_images table
    # Check if products have images that need migration
    cursor.execute('SELECT id, image FROM products WHERE image IS NOT NULL AND image != "default.jpg"')
    products = cursor.fetchall()
    
    migrated = 0
    for product in products:
        product_id, image = product
        # Check if already migrated
        existing = cursor.execute('SELECT id FROM product_images WHERE product_id = ? AND image_path = ?', 
                                  (product_id, image)).fetchone()
        if not existing:
            cursor.execute('''
                INSERT INTO product_images (product_id, image_path, display_order)
                VALUES (?, ?, 0)
            ''', (product_id, image))
            migrated += 1
    
    if migrated > 0:
        print(f"✅ Migrated {migrated} existing product images")
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print("✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == '__main__':
    migrate_database()