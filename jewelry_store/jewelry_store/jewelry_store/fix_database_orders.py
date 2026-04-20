import sqlite3

conn = sqlite3.connect('jewelry.db')
cursor = conn.cursor()

# Check if payment_status column exists
cursor.execute("PRAGMA table_info(orders)")
columns = [col[1] for col in cursor.fetchall()]

print("=" * 50)
print("DATABASE FIX")
print("=" * 50)

if 'payment_status' not in columns:
    print("Adding payment_status column...")
    cursor.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'pending'")
    print("✅ Column added!")
else:
    print("✅ payment_status column already exists")

if 'receipt_image' not in columns:
    print("Adding receipt_image column...")
    cursor.execute("ALTER TABLE orders ADD COLUMN receipt_image TEXT")
    print("✅ Column added!")
else:
    print("✅ receipt_image column already exists")

# Update existing orders
cursor.execute("UPDATE orders SET payment_status = 'pending' WHERE payment_status IS NULL")
cursor.execute("UPDATE orders SET payment_status = 'confirmed' WHERE payment_method = 'cod'")

conn.commit()

# Show current orders
print("\n" + "=" * 50)
print("CURRENT ORDERS")
print("=" * 50)
orders = cursor.execute('SELECT id, order_number, total_amount, payment_method, payment_status FROM orders').fetchall()
if orders:
    for order in orders:
        print(f"ID: {order[0]}, Order: {order[1]}, Total: ₨ {order[2]}, Method: {order[3]}, Payment Status: {order[4]}")
else:
    print("No orders found")

print("\n✅ Database fixed successfully!")
conn.close()