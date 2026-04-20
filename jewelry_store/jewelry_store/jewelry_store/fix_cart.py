import sqlite3

conn = sqlite3.connect('jewelry.db')
cursor = conn.cursor()

# View current cart items
print("=" * 50)
print("CURRENT CART ITEMS")
print("=" * 50)
cart = cursor.execute('SELECT id, session_id, product_id, product_name, quantity FROM cart').fetchall()
if cart:
    for item in cart:
        print(f"ID: {item[0]}, Session: {item[1]}, Product ID: {item[2]}, Name: {item[3]}, Qty: {item[4]}")
else:
    print("No items in cart")

# Clear all cart items to fix double price issue
cursor.execute('DELETE FROM cart')
conn.commit()

print("\n" + "=" * 50)
print("✅ Cart cleared successfully!")
print("=" * 50)

conn.close()