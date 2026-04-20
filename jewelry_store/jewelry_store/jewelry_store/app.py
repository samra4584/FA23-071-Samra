from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from functools import wraps
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'elite-sparkle-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configuration
UPLOAD_FOLDER = 'static/uploads'
PRODUCT_IMAGES_FOLDER = 'static/product_images'
RECEIPTS_FOLDER = 'static/receipts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PRODUCT_IMAGES_FOLDER, exist_ok=True)
os.makedirs(RECEIPTS_FOLDER, exist_ok=True)

# Admin credentials
ADMIN_USERNAME = 'Qasim1204'
ADMIN_PASSWORD = 'Qasim120420$'

# Delivery charge per item
DELIVERY_CHARGE_PER_ITEM = 250

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'elitesparkleofficial1204@gmail.com'
EMAIL_PASSWORD = 'xeem yrdv gfal bqmc'
SITE_URL = 'http://127.0.0.1:5000'

def send_email(to_email, subject, body_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_password_change_email(email, first_name):
    """Send email notification when password is changed"""
    subject = "Password Changed - Elite Sparkle"
    body = f"""
    <html>
    <body>
        <div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;background:#0a0a0a;color:white;">
            <h1 style="color:#d4af37;">🔐 Password Changed</h1>
            <p>Dear {first_name},</p>
            <p>Your Elite Sparkle account password has been successfully changed.</p>
            <p>If you did not make this change, please contact us immediately.</p>
            <hr style="border-color:#d4af37;">
            <p style="font-size:12px;color:#888;">If this wasn't you, please reset your password immediately.</p>
        </div>
    </body>
    </html>
    """
    return send_email(email, subject, body)

def send_order_email(order_id, status):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    if not order:
        return False
    
    if status == 'placed':
        subject = f"Order Confirmation #{order['order_number']} - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">✨ Order Confirmed!</h1>
            <p>Dear {order['first_name']},</p>
            <p>Your order #{order['order_number']} has been placed successfully!</p>
            <p>Subtotal: ₨ {order['subtotal']}</p>
            <p>Delivery Charge: ₨ {order['delivery_charge']}</p>
            <p>Total Amount: ₨ {order['total_amount']}</p>
            <p>Payment: {order['payment_method']}</p>
            <a href="{SITE_URL}/my_orders">View Orders</a>
        </div></body></html>
        """
    elif status == 'shipped':
        subject = f"Order #{order['order_number']} Shipped - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">🚚 Order Shipped!</h1>
            <p>Dear {order['first_name']},</p>
            <p>Your order #{order['order_number']} has been shipped!</p>
            <a href="{SITE_URL}/my_orders">Track Order</a>
        </div></body></html>
        """
    elif status == 'delivered':
        subject = f"Order #{order['order_number']} Delivered - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">🎉 Order Delivered!</h1>
            <p>Dear {order['first_name']},</p>
            <p>Your order #{order['order_number']} has been delivered!</p>
            <a href="{SITE_URL}/write_review/{order_id}">Write a Review</a>
        </div></body></html>
        """
    elif status == 'cancelled':
        subject = f"Order #{order['order_number']} Cancelled - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:600px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">❌ Order Cancelled</h1>
            <p>Dear {order['first_name']},</p>
            <p>Your order #{order['order_number']} has been cancelled.</p>
        </div></body></html>
        """
    else:
        return False
    return send_email(order['email'], subject, body)

def send_otp_email(to_email, otp_code, otp_type='registration'):
    if otp_type == 'registration':
        subject = "Verify Your Email - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:500px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">✨ Elite Sparkle</h1>
            <p>Your OTP: <strong>{otp_code}</strong></p>
            <p>Valid for 10 minutes.</p>
        </div></body></html>
        """
    else:
        subject = "Password Reset OTP - Elite Sparkle"
        body = f"""
        <html><body><div style="max-width:500px;margin:0 auto;padding:20px;border:2px solid #d4af37;border-radius:10px;">
            <h1 style="color:#d4af37;">✨ Elite Sparkle</h1>
            <p>Your OTP for password reset: <strong>{otp_code}</strong></p>
            <p>Valid for 10 minutes.</p>
        </div></body></html>
        """
    return send_email(to_email, subject, body)

def send_review_notification(product_id, user_id, rating, comment):
    """Send notification to admin when a review is added"""
    conn = get_db()
    product = conn.execute('SELECT name FROM products WHERE id = ?', (product_id,)).fetchone()
    user = conn.execute('SELECT first_name, last_name FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if product and user:
        message = f"⭐ New {rating}-star review on '{product['name']}' by {user['first_name']} {user['last_name']}"
        conn = get_db()
        conn.execute('''
            INSERT INTO notifications (type, message, name, email, is_read)
            VALUES (?, ?, ?, ?, ?)
        ''', ('review', message, user['first_name'] + ' ' + user['last_name'], None, 0))
        conn.commit()
        conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    conn = sqlite3.connect('jewelry.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = sqlite3.connect('jewelry.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS site_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS product_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        display_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS temp_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        otp TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (datetime('now', '+10 minutes')))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (datetime('now', '+10 minutes')))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        landmark TEXT,
        city TEXT NOT NULL,
        postal_code TEXT,
        delivery_instructions TEXT,
        payment_method TEXT NOT NULL,
        subtotal REAL DEFAULT 0,
        delivery_charge REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        payment_status TEXT DEFAULT 'pending',
        receipt_image TEXT,
        review_sent INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER DEFAULT 1,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        title TEXT,
        comment TEXT NOT NULL,
        status TEXT DEFAULT 'approved',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    
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
    
    # Insert sample products if none exist
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('💎 Diamond Solitaire Ring', 2950, 'rings', 'Beautiful diamond solitaire ring. Perfect for engagements.', 'diamond_ring.jpg'),
            ('📿 Pearl Necklace', 1899, 'necklaces', 'Beautiful freshwater pearl necklace.', 'pearl_necklace.jpg'),
            ('✨ Gold Hoop Earrings', 799, 'earrings', '14K gold plated hoop earrings.', 'gold_hoops.jpg'),
            ('🔗 Silver Bracelet', 499, 'bracelets', 'Sterling silver elegant bracelet.', 'silver_bracelet.jpg'),
            ('🕐 Luxury Gold Watch', 4999, 'watches', 'Premium gold plated watch.', 'gold_watch.jpg'),
            ('👑 Royal Bridal Set', 12999, 'sets', 'Complete bridal jewelry set.', 'bridal_set.jpg'),
        ]
        for product in sample_products:
            cursor.execute('''
                INSERT INTO products (name, price, category, description, image)
                VALUES (?, ?, ?, ?, ?)
            ''', product)
        print("✅ Sample products added!")
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

create_tables()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please login first!', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please login or create an account to continue!', 'error')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== CUSTOMER ROUTES ==========

@app.route('/')
def index():
    conn = get_db()
    all_products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    
    products_by_category = {
        'rings': [], 'necklaces': [], 'earrings': [], 
        'bracelets': [], 'watches': [], 'pendants': [], 'sets': []
    }
    
    for product in all_products:
        product_dict = dict(product)
        first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                  (product['id'],)).fetchone()
        if first_image:
            product_dict['display_image'] = first_image['image_path']
        elif product['image'] and product['image'] != 'default.jpg':
            product_dict['display_image'] = product['image']
        else:
            product_dict['display_image'] = None
        
        avg_rating = conn.execute('SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                  (product['id'],)).fetchone()[0]
        review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                    (product['id'],)).fetchone()[0]
        product_dict['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        product_dict['review_count'] = review_count
        
        category = product['category']
        if category in products_by_category:
            products_by_category[category].append(product_dict)
    
    conn.close()
    
    conn = get_db()
    logo = conn.execute('SELECT setting_value FROM site_settings WHERE setting_key = "logo"').fetchone()
    cover_photo = conn.execute('SELECT setting_value FROM site_settings WHERE setting_key = "cover_photo"').fetchone()
    conn.close()
    
    return render_template('index.html', 
                         products_by_category=products_by_category,
                         logo=logo['setting_value'] if logo else None,
                         cover_photo=cover_photo['setting_value'] if cover_photo else None)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db()
    products = conn.execute('''
        SELECT * FROM products 
        WHERE name LIKE ? OR category LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    products_list = []
    for product in products:
        product_dict = dict(product)
        first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                  (product['id'],)).fetchone()
        if first_image:
            product_dict['display_image'] = first_image['image_path']
        elif product['image'] and product['image'] != 'default.jpg':
            product_dict['display_image'] = product['image']
        else:
            product_dict['display_image'] = None
        
        avg_rating = conn.execute('SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                  (product['id'],)).fetchone()[0]
        review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                    (product['id'],)).fetchone()[0]
        product_dict['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        product_dict['review_count'] = review_count
        products_list.append(product_dict)
    
    conn.close()
    return render_template('search_results.html', products=products_list, query=query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return redirect(url_for('index'))
    
    images_data = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order', 
                               (product_id,)).fetchall()
    images_list = [img['image_path'] for img in images_data]
    
    if len(images_list) == 0 and product['image'] and product['image'] != 'default.jpg':
        images_list.append(product['image'])
    
    product_dict = dict(product)
    
    reviews = conn.execute('''
        SELECT r.*, u.first_name, u.last_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.product_id = ? AND r.status = 'approved' 
        ORDER BY r.created_at DESC
    ''', (product_id,)).fetchall()
    
    avg_rating = conn.execute('SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = ? AND status = "approved"', 
                              (product_id,)).fetchone()[0]
    review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                (product_id,)).fetchone()[0]
    conn.close()
    
    return render_template('product_detail.html', 
                         product=product_dict,
                         images=images_list,
                         reviews=reviews,
                         avg_rating=round(avg_rating, 1) if avg_rating else 0,
                         review_count=review_count)

@app.route('/category/<category>')
@app.route('/category/<category>/page/<int:page>')
def category_view(category, page=1):
    per_page = 6
    offset = (page - 1) * per_page
    
    conn = get_db()
    total_products = conn.execute('SELECT COUNT(*) FROM products WHERE category = ?', (category,)).fetchone()[0]
    products = conn.execute('SELECT * FROM products WHERE category = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                           (category, per_page, offset)).fetchall()
    
    products_list = []
    for product in products:
        product_dict = dict(product)
        first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                  (product['id'],)).fetchone()
        if first_image:
            product_dict['display_image'] = first_image['image_path']
        elif product['image'] and product['image'] != 'default.jpg':
            product_dict['display_image'] = product['image']
        else:
            product_dict['display_image'] = None
        
        avg_rating = conn.execute('SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                  (product['id'],)).fetchone()[0]
        review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                    (product['id'],)).fetchone()[0]
        product_dict['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        product_dict['review_count'] = review_count
        products_list.append(product_dict)
    
    conn.close()
    total_pages = (total_products + per_page - 1) // per_page
    
    return render_template('category.html', 
                         products=products_list, 
                         category=category,
                         page=page, 
                         total_pages=total_pages,
                         total_products=total_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))
        
        conn = get_db()
        existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            flash('Email already registered! Please login.', 'error')
            conn.close()
            return redirect(url_for('user_login'))
        
        otp = str(random.randint(100000, 999999))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn.execute('DELETE FROM temp_users WHERE email = ?', (email,))
        conn.execute('''
            INSERT INTO temp_users (first_name, last_name, email, phone, password, otp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, hashed_password, otp))
        conn.commit()
        conn.close()
        
        if send_otp_email(email, otp, 'registration'):
            session['temp_email'] = email
            flash('✅ OTP sent to your email! Please verify.', 'success')
            return redirect(url_for('verify_register_otp'))
        else:
            flash('❌ Failed to send OTP. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/verify_register_otp', methods=['GET', 'POST'])
def verify_register_otp():
    if 'temp_email' not in session:
        flash('Please register first!', 'error')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        email = session['temp_email']
        otp_entered = request.form['otp']
        
        conn = get_db()
        temp_user = conn.execute('''
            SELECT * FROM temp_users 
            WHERE email = ? AND otp = ? AND datetime(expires_at) > datetime('now')
        ''', (email, otp_entered)).fetchone()
        
        if temp_user:
            conn.execute('''
                INSERT INTO users (first_name, last_name, email, phone, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (temp_user['first_name'], temp_user['last_name'], 
                  temp_user['email'], temp_user['phone'], temp_user['password']))
            conn.execute('DELETE FROM temp_users WHERE email = ?', (email,))
            conn.commit()
            conn.close()
            session.pop('temp_email', None)
            flash('✅ Email verified! Registration completed. Please login.', 'success')
            return redirect(url_for('user_login'))
        else:
            flash('❌ Invalid or expired OTP!', 'error')
        conn.close()
    
    return render_template('verify_register_otp.html')

@app.route('/resend_register_otp')
def resend_register_otp():
    if 'temp_email' not in session:
        return redirect(url_for('register'))
    
    email = session['temp_email']
    otp = str(random.randint(100000, 999999))
    
    conn = get_db()
    conn.execute('UPDATE temp_users SET otp = ?, expires_at = datetime("now", "+10 minutes") WHERE email = ?', 
                (otp, email))
    conn.commit()
    conn.close()
    
    if send_otp_email(email, otp, 'registration'):
        flash('✅ New OTP sent!', 'success')
    else:
        flash('❌ Failed to send OTP.', 'error')
    
    return redirect(url_for('verify_register_otp'))

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                           (email, hashed_password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = f"{user['first_name']} {user['last_name']}"
            session['user_email'] = user['email']
            session['user_phone'] = user['phone']
            session['user_first_name'] = user['first_name']
            session['user_last_name'] = user['last_name']
            flash(f'Welcome back {user["first_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('user_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@user_login_required
def profile():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()
    
    if request.method == 'POST':
        # Update profile information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        if first_name and last_name and phone:
            conn.execute('''
                UPDATE users SET first_name = ?, last_name = ?, phone = ?
                WHERE id = ?
            ''', (first_name, last_name, phone, session['user_id']))
            conn.commit()
            
            # Update session
            session['user_name'] = f"{first_name} {last_name}"
            session['user_first_name'] = first_name
            session['user_last_name'] = last_name
            session['user_phone'] = phone
            
            flash('✅ Profile updated successfully!', 'success')
        
        conn.close()
        return redirect(url_for('profile'))
    
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/update_password', methods=['POST'])
@user_login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('❌ New passwords do not match!', 'error')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('❌ Password must be at least 6 characters!', 'error')
        return redirect(url_for('profile'))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
    
    if user['password'] != hashed_current:
        flash('❌ Current password is incorrect!', 'error')
        conn.close()
        return redirect(url_for('profile'))
    
    # Update password
    hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
    conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_new, session['user_id']))
    conn.commit()
    
    # Send email notification
    send_password_change_email(user['email'], user['first_name'])
    
    conn.close()
    
    flash('✅ Password changed successfully! A confirmation email has been sent.', 'success')
    return redirect(url_for('profile'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            otp = str(random.randint(100000, 999999))
            conn.execute('DELETE FROM password_resets WHERE email = ?', (email,))
            conn.execute('INSERT INTO password_resets (email, otp) VALUES (?, ?)', (email, otp))
            conn.commit()
            
            if send_otp_email(email, otp, 'password_reset'):
                session['reset_email'] = email
                flash('✅ OTP sent to your email!', 'success')
                return redirect(url_for('verify_otp'))
            else:
                flash('❌ Failed to send OTP.', 'error')
        else:
            flash('❌ Email not found!', 'error')
        conn.close()
    
    return render_template('forgot_password.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        flash('Please request OTP first!', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        email = session['reset_email']
        otp_entered = request.form['otp']
        
        conn = get_db()
        reset_record = conn.execute('''
            SELECT * FROM password_resets 
            WHERE email = ? AND otp = ? AND datetime(expires_at) > datetime('now')
        ''', (email, otp_entered)).fetchone()
        
        if reset_record:
            conn.execute('DELETE FROM password_resets WHERE email = ?', (email,))
            conn.commit()
            conn.close()
            session['verified_email'] = email
            flash('✅ OTP verified! Set new password.', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('❌ Invalid or expired OTP!', 'error')
        conn.close()
    
    return render_template('verify_otp.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'verified_email' not in session:
        flash('Please verify OTP first!', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('❌ Passwords do not match!', 'error')
            return redirect(url_for('reset_password'))
        
        if len(new_password) < 6:
            flash('❌ Password must be at least 6 characters!', 'error')
            return redirect(url_for('reset_password'))
        
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        email = session['verified_email']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
        conn.commit()
        conn.close()
        
        # Send email notification
        if user:
            send_password_change_email(email, user['first_name'])
        
        session.pop('verified_email', None)
        session.pop('reset_email', None)
        
        flash('✅ Password reset successful! A confirmation email has been sent. Please login.', 'success')
        return redirect(url_for('user_login'))
    
    return render_template('reset_password.html')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if product:
        session_id = request.remote_addr
        existing = conn.execute('SELECT * FROM cart WHERE session_id = ? AND product_id = ?',
                               (session_id, product_id)).fetchone()
        
        first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                  (product_id,)).fetchone()
        cart_image = first_image['image_path'] if first_image else product['image']
        
        if existing:
            new_quantity = existing['quantity'] + quantity
            conn.execute('UPDATE cart SET quantity = ? WHERE id = ?', (new_quantity, existing['id']))
            flash(f'Updated {product["name"]} quantity to {new_quantity}!', 'success')
        else:
            conn.execute('''
                INSERT INTO cart (session_id, product_id, product_name, price, quantity, image)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, product_id, product['name'], product['price'], quantity, cart_image))
            flash(f'{product["name"]} added to cart!', 'success')
        
        conn.commit()
    
    conn.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    session_id = request.remote_addr
    conn = get_db()
    cart_items = conn.execute('SELECT * FROM cart WHERE session_id = ?', (session_id,)).fetchall()
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)
    delivery_charge = total_items * DELIVERY_CHARGE_PER_ITEM
    grand_total = subtotal + delivery_charge
    
    conn.close()
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal,
                         delivery_charge=delivery_charge,
                         grand_total=grand_total,
                         total_items=total_items,
                         delivery_charge_per_item=DELIVERY_CHARGE_PER_ITEM)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    quantity = int(request.form['quantity'])
    if quantity <= 0:
        conn = get_db()
        conn.execute('DELETE FROM cart WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
    else:
        conn = get_db()
        conn.execute('UPDATE cart SET quantity = ? WHERE id = ?', (quantity, item_id))
        conn.commit()
        conn.close()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    conn = get_db()
    conn.execute('DELETE FROM cart WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@user_login_required
def checkout():
    session_id = request.remote_addr
    conn = get_db()
    cart_items = conn.execute('SELECT * FROM cart WHERE session_id = ?', (session_id,)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)
    delivery_charge = total_items * DELIVERY_CHARGE_PER_ITEM
    grand_total = subtotal + delivery_charge
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        landmark = request.form.get('landmark', '')
        city = request.form['city']
        postal_code = request.form.get('postal_code', '')
        delivery_instructions = request.form.get('instructions', '')
        payment_method = request.form['payment_method']
        
        receipt_filename = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                receipt_filename = timestamp + filename
                file.save(os.path.join('static/receipts', receipt_filename))
        
        order_number = f"ELITE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor = conn.execute('''
            INSERT INTO orders (order_number, user_id, first_name, last_name, email, phone, address, landmark, city, postal_code, delivery_instructions, payment_method, subtotal, delivery_charge, total_amount, receipt_image, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_number, session.get('user_id'), first_name, last_name, email, phone, address, landmark, city, postal_code, delivery_instructions, payment_method, subtotal, delivery_charge, grand_total, receipt_filename, 'pending'))
        
        order_id = cursor.lastrowid
        
        for item in cart_items:
            conn.execute('''
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['product_name'], item['quantity'], item['price']))
        
        conn.execute('DELETE FROM cart WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        
        send_order_email(order_id, 'placed')
        
        flash(f'Order placed successfully! Order number: {order_number}', 'success')
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    conn.close()
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal,
                         delivery_charge=delivery_charge,
                         grand_total=grand_total,
                         total_items=total_items)

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    conn.close()
    return render_template('order_confirmation.html', order=order, items=items)

@app.route('/my_orders')
@user_login_required
def my_orders():
    conn = get_db()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', 
                         (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('my_orders.html', orders=orders)

@app.route('/write_review/<int:order_id>', methods=['GET', 'POST'])
@user_login_required
def write_review(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ? AND user_id = ?', 
                        (order_id, session.get('user_id'))).fetchone()
    
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('my_orders'))
    
    order_items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        rating = int(request.form['rating'])
        title = request.form.get('title', '')
        comment = request.form['comment']
        
        existing = conn.execute('SELECT id FROM reviews WHERE product_id = ? AND user_id = ?', 
                               (product_id, session.get('user_id'))).fetchone()
        
        if existing:
            flash('You have already reviewed this product!', 'error')
        else:
            conn.execute('''
                INSERT INTO reviews (product_id, user_id, rating, title, comment, status)
                VALUES (?, ?, ?, ?, ?, 'approved')
            ''', (product_id, session.get('user_id'), rating, title, comment))
            conn.commit()
            
            send_review_notification(product_id, session.get('user_id'), rating, comment)
            
            flash('✅ Thank you for your review!', 'success')
        
        conn.close()
        return redirect(url_for('product_detail', product_id=product_id))
    
    conn.close()
    return render_template('write_review.html', order=order, order_items=order_items)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if name and email and message:
            conn = get_db()
            conn.execute('''
                INSERT INTO notifications (type, message, name, email, is_read)
                VALUES (?, ?, ?, ?, ?)
            ''', ('contact', message, name, email, 0))
            conn.commit()
            conn.close()
            flash('✅ Thank you for your message! We will get back to you soon.', 'success')
        else:
            flash('❌ Please fill all fields.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# ========== ADMIN PRODUCTS MANAGEMENT ==========

@app.route('/admin/products')
@login_required
def admin_products():
    conn = get_db()
    
    filter_category = request.args.get('category', 'all')
    
    categories = ['rings', 'necklaces', 'earrings', 'bracelets', 'watches', 'pendants', 'sets']
    products_by_category = {}
    
    if filter_category == 'all':
        for category in categories:
            products = conn.execute('SELECT * FROM products WHERE category = ? ORDER BY created_at DESC', (category,)).fetchall()
            products_list = []
            for product in products:
                product_dict = dict(product)
                first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                          (product['id'],)).fetchone()
                product_dict['display_image'] = first_image['image_path'] if first_image else product['image']
                products_list.append(product_dict)
            products_by_category[category] = products_list
    else:
        if filter_category in categories:
            products = conn.execute('SELECT * FROM products WHERE category = ? ORDER BY created_at DESC', (filter_category,)).fetchall()
            products_list = []
            for product in products:
                product_dict = dict(product)
                first_image = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order LIMIT 1', 
                                          (product['id'],)).fetchone()
                product_dict['display_image'] = first_image['image_path'] if first_image else product['image']
                products_list.append(product_dict)
            products_by_category[filter_category] = products_list
            for cat in categories:
                if cat != filter_category:
                    products_by_category[cat] = []
    
    conn.close()
    return render_template('admin_products.html', 
                         products_by_category=products_by_category, 
                         categories=categories,
                         current_category=filter_category)

# ========== ADMIN ORDERS MANAGEMENT ==========

@app.route('/admin/orders')
@login_required
def admin_orders():
    conn = get_db()
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        orders = conn.execute('SELECT * FROM orders WHERE order_number LIKE ? ORDER BY created_at DESC', 
                             (f'%{search_query}%',)).fetchall()
    else:
        orders = conn.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    
    conn.close()
    return render_template('admin_orders.html', orders=orders, current_status=None)

@app.route('/admin/orders/<status>')
@login_required
def admin_orders_by_status(status):
    conn = get_db()
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        orders = conn.execute('SELECT * FROM orders WHERE status = ? AND order_number LIKE ? ORDER BY created_at DESC', 
                             (status, f'%{search_query}%')).fetchall()
    else:
        orders = conn.execute('SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC', (status,)).fetchall()
    
    conn.close()
    return render_template('admin_orders.html', orders=orders, current_status=status)

# ========== API ROUTES ==========

@app.route('/api/product/<int:product_id>')
def api_product_detail(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    images_data = conn.execute('SELECT image_path FROM product_images WHERE product_id = ? ORDER BY display_order', 
                               (product_id,)).fetchall()
    images_list = [img['image_path'] for img in images_data]
    
    if len(images_list) == 0 and product['image'] and product['image'] != 'default.jpg':
        images_list.append(product['image'])
    
    avg_rating = conn.execute('SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = ? AND status = "approved"', 
                              (product_id,)).fetchone()[0]
    review_count = conn.execute('SELECT COUNT(*) FROM reviews WHERE product_id = ? AND status = "approved"', 
                                (product_id,)).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'category': product['category'],
        'description': product['description'],
        'images': images_list,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'review_count': review_count
    })

@app.route('/api/order_items/<int:order_id>')
@login_required
def api_order_items(order_id):
    conn = get_db()
    items = conn.execute('SELECT product_name, quantity, price FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/api/notifications/unread')
@login_required
def api_unread_notifications():
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0').fetchone()[0]
    notifications = conn.execute('SELECT id, type, message, name, email, created_at FROM notifications WHERE is_read = 0 ORDER BY created_at DESC LIMIT 10').fetchall()
    conn.close()
    return jsonify({
        'count': count,
        'notifications': [dict(n) for n in notifications]
    })

@app.route('/api/notifications/mark_read/<int:notification_id>')
@login_required
def api_mark_notification_read(notification_id):
    conn = get_db()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/notifications/mark_all_read')
@login_required
def api_mark_all_notifications_read():
    conn = get_db()
    conn.execute('UPDATE notifications SET is_read = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ========== ADMIN ROUTES ==========

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    conn = get_db()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    orders = conn.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    reviews = conn.execute('SELECT * FROM reviews ORDER BY created_at DESC').fetchall()
    unread_notifications = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0').fetchone()[0]
    notifications = conn.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', 
                         products=products, 
                         orders=orders, 
                         users=users, 
                         reviews=reviews,
                         unread_notifications=unread_notifications,
                         notifications=notifications)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        description = request.form['description']
        
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO products (name, price, category, description, image)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, category, description, 'default.jpg'))
        product_id = cursor.lastrowid
        
        if 'product_images' in request.files:
            files = request.files.getlist('product_images')
            display_order = 0
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    image_filename = timestamp + '_' + filename
                    file.save(os.path.join(PRODUCT_IMAGES_FOLDER, image_filename))
                    conn.execute('''
                        INSERT INTO product_images (product_id, image_path, display_order)
                        VALUES (?, ?, ?)
                    ''', (product_id, image_filename, display_order))
                    
                    if display_order == 0:
                        conn.execute('UPDATE products SET image = ? WHERE id = ?', (image_filename, product_id))
                    
                    display_order += 1
        
        conn.commit()
        conn.close()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_add.html')

@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    images = conn.execute('SELECT * FROM product_images WHERE product_id = ? ORDER BY display_order', 
                         (product_id,)).fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        description = request.form['description']
        
        conn.execute('''
            UPDATE products 
            SET name = ?, price = ?, category = ?, description = ?
            WHERE id = ?
        ''', (name, price, category, description, product_id))
        
        if 'additional_images' in request.files:
            files = request.files.getlist('additional_images')
            max_order = conn.execute('SELECT COALESCE(MAX(display_order), -1) FROM product_images WHERE product_id = ?', 
                                    (product_id,)).fetchone()[0]
            display_order = max_order + 1
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    image_filename = timestamp + '_' + filename
                    file.save(os.path.join(PRODUCT_IMAGES_FOLDER, image_filename))
                    conn.execute('''
                        INSERT INTO product_images (product_id, image_path, display_order)
                        VALUES (?, ?, ?)
                    ''', (product_id, image_filename, display_order))
                    display_order += 1
        
        conn.commit()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    conn.close()
    return render_template('admin_edit.html', product=product, images=images)

@app.route('/admin/delete_image/<int:image_id>')
@login_required
def admin_delete_image(image_id):
    conn = get_db()
    image = conn.execute('SELECT * FROM product_images WHERE id = ?', (image_id,)).fetchone()
    if image:
        image_path = os.path.join(PRODUCT_IMAGES_FOLDER, image['image_path'])
        if os.path.exists(image_path):
            os.remove(image_path)
        conn.execute('DELETE FROM product_images WHERE id = ?', (image_id,))
        conn.commit()
        flash('Image deleted successfully!', 'success')
    conn.close()
    return redirect(request.referrer or url_for('admin_products'))

@app.route('/admin/delete/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    conn = get_db()
    images = conn.execute('SELECT image_path FROM product_images WHERE product_id = ?', (product_id,)).fetchall()
    for img in images:
        img_path = os.path.join(PRODUCT_IMAGES_FOLDER, img['image_path'])
        if os.path.exists(img_path):
            os.remove(img_path)
    conn.execute('DELETE FROM product_images WHERE product_id = ?', (product_id,))
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    status = request.form['status']
    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
    if status in ['shipped', 'delivered', 'cancelled']:
        send_order_email(order_id, status)
    
    flash(f'Order status updated to {status}!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/confirm_payment/<int:order_id>')
@login_required
def admin_confirm_payment(order_id):
    conn = get_db()
    conn.execute('UPDATE orders SET payment_status = "confirmed" WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    flash('✅ Payment confirmed!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/view_order/<int:order_id>')
@login_required
def admin_view_order(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    conn.close()
    return render_template('admin_order_detail.html', order=order, items=items)

@app.route('/admin/delete_order/<int:order_id>')
@login_required
def admin_delete_order(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order:
        conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
        conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        flash(f'✅ Order #{order["order_number"]} deleted!', 'success')
    else:
        flash('Order not found!', 'error')
    conn.close()
    return redirect(url_for('admin_orders'))

@app.route('/admin/delete_delivered_orders')
@login_required
def admin_delete_delivered_orders():
    conn = get_db()
    delivered_orders = conn.execute('SELECT id, order_number FROM orders WHERE status = "delivered"').fetchall()
    if delivered_orders:
        for order in delivered_orders:
            conn.execute('DELETE FROM order_items WHERE order_id = ?', (order['id'],))
            conn.execute('DELETE FROM orders WHERE id = ?', (order['id'],))
        conn.commit()
        flash(f'✅ {len(delivered_orders)} delivered orders deleted!', 'success')
    else:
        flash('No delivered orders found.', 'info')
    conn.close()
    return redirect(url_for('admin_orders'))

@app.route('/admin/search_order', methods=['GET', 'POST'])
@login_required
def admin_search_order():
    order = None
    order_items = []
    if request.method == 'POST':
        order_number = request.form.get('order_number', '').strip()
        if order_number:
            conn = get_db()
            order = conn.execute('SELECT * FROM orders WHERE order_number LIKE ?', (f'%{order_number}%',)).fetchone()
            if order:
                order_items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],)).fetchall()
            else:
                flash(f'Order #{order_number} not found!', 'error')
            conn.close()
    return render_template('admin_search_order.html', order=order, order_items=order_items)

@app.route('/admin/users')
@login_required
def admin_users():
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users, orders=orders)

@app.route('/admin/user_orders/<int:user_id>')
@login_required
def admin_user_orders(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return render_template('admin_user_orders.html', user=user, orders=orders)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        
        new_password = request.form.get('new_password')
        if new_password and len(new_password) >= 6:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            conn.execute('''
                UPDATE users SET first_name = ?, last_name = ?, email = ?, phone = ?, password = ?
                WHERE id = ?
            ''', (first_name, last_name, email, phone, hashed_password, user_id))
        else:
            conn.execute('''
                UPDATE users SET first_name = ?, last_name = ?, email = ?, phone = ?
                WHERE id = ?
            ''', (first_name, last_name, email, phone, user_id))
        
        conn.commit()
        conn.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    conn.close()
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def admin_delete_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        order_count = conn.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,)).fetchone()[0]
        if order_count > 0:
            flash(f'❌ User has {order_count} orders. Use "Force Delete".', 'error')
        else:
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            flash(f'✅ User "{user["first_name"]} {user["last_name"]}" deleted!', 'success')
    else:
        flash('User not found!', 'error')
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user_force/<int:user_id>')
@login_required
def admin_delete_user_force(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        orders = conn.execute('SELECT id FROM orders WHERE user_id = ?', (user_id,)).fetchall()
        for order in orders:
            conn.execute('DELETE FROM order_items WHERE order_id = ?', (order['id'],))
            conn.execute('DELETE FROM orders WHERE id = ?', (order['id'],))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash(f'✅ User "{user["first_name"]} {user["last_name"]}" and {len(orders)} orders deleted!', 'success')
    else:
        flash('User not found!', 'error')
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/export_users_excel')
@login_required
def admin_export_users_excel():
    conn = get_db()
    users = conn.execute('SELECT id, first_name, last_name, email, phone, created_at FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['User ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 'Registration Date'])
    for user in users:
        writer.writerow([user['id'], user['first_name'], user['last_name'], user['email'], user['phone'], user['created_at']])
    
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=elite_sparkle_users.csv'})

@app.route('/admin/reviews')
@login_required
def admin_reviews():
    conn = get_db()
    reviews = conn.execute('''
        SELECT r.*, u.first_name, u.last_name, p.name as product_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN products p ON r.product_id = p.id
        ORDER BY r.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_reviews.html', reviews=reviews)

@app.route('/admin/delete_review/<int:review_id>')
@login_required
def admin_delete_review(review_id):
    conn = get_db()
    conn.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
    conn.commit()
    conn.close()
    flash('Review deleted!', 'success')
    return redirect(url_for('admin_reviews'))

@app.route('/admin/notifications')
@login_required
def admin_notifications():
    conn = get_db()
    notifications = conn.execute('SELECT * FROM notifications ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_notifications.html', notifications=notifications)

@app.route('/admin/site_settings', methods=['GET', 'POST'])
@login_required
def admin_site_settings():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    if request.method == 'POST':
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                logo_filename = timestamp + filename
                file.save(os.path.join('static/uploads', logo_filename))
                cursor.execute('INSERT OR REPLACE INTO site_settings (setting_key, setting_value) VALUES (?, ?)', ('logo', logo_filename))
                conn.commit()
                flash('✅ Logo uploaded!', 'success')
        
        if 'cover_photo' in request.files:
            file = request.files['cover_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                cover_filename = timestamp + filename
                file.save(os.path.join('static/uploads', cover_filename))
                cursor.execute('INSERT OR REPLACE INTO site_settings (setting_key, setting_value) VALUES (?, ?)', ('cover_photo', cover_filename))
                conn.commit()
                flash('✅ Cover photo uploaded!', 'success')
        
        conn.close()
        return redirect(url_for('admin_site_settings'))
    
    logo = conn.execute('SELECT setting_value FROM site_settings WHERE setting_key = "logo"').fetchone()
    cover_photo = conn.execute('SELECT setting_value FROM site_settings WHERE setting_key = "cover_photo"').fetchone()
    conn.close()
    
    return render_template('admin_site_settings.html', 
                         logo=logo['setting_value'] if logo else None,
                         cover_photo=cover_photo['setting_value'] if cover_photo else None)

@app.route('/admin/remove_logo')
@login_required
def admin_remove_logo():
    conn = get_db()
    conn.execute('DELETE FROM site_settings WHERE setting_key = "logo"')
    conn.commit()
    conn.close()
    flash('✅ Logo removed!', 'success')
    return redirect(url_for('admin_site_settings'))

@app.route('/admin/remove_cover')
@login_required
def admin_remove_cover():
    conn = get_db()
    conn.execute('DELETE FROM site_settings WHERE setting_key = "cover_photo"')
    conn.commit()
    conn.close()
    flash('✅ Cover photo removed!', 'success')
    return redirect(url_for('admin_site_settings'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)