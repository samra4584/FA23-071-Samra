def get_email_template(template_name, **kwargs):
    """Return HTML email template with gold theme"""
    
    base_style = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0a0a0a;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: linear-gradient(135deg, #1a1a2e, #0a0a0a);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
        }
        .header {
            border-bottom: 1px solid #d4af37;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #d4af37;
            font-size: 28px;
            margin: 0;
        }
        .header p {
            color: #888;
            font-size: 12px;
            margin-top: 5px;
        }
        .content {
            color: #fff;
            line-height: 1.6;
        }
        .otp-code {
            font-size: 42px;
            font-weight: bold;
            color: #d4af37;
            background: rgba(212,175,55,0.1);
            padding: 20px;
            border-radius: 10px;
            letter-spacing: 5px;
            margin: 20px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #d4af37;
            color: #0a0a0a;
            text-decoration: none;
            border-radius: 40px;
            font-weight: bold;
            margin: 20px 0;
        }
        .footer {
            border-top: 1px solid rgba(212,175,55,0.3);
            padding-top: 20px;
            margin-top: 20px;
            font-size: 11px;
            color: #888;
        }
        .order-details {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: left;
        }
        .star-rating {
            color: #d4af37;
            font-size: 24px;
            letter-spacing: 5px;
        }
    </style>
    """
    
    if template_name == 'registration_otp':
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ ELITE SPARKLE ✨</h1>
                    <p>Luxury Jewelry Pakistan</p>
                </div>
                <div class="content">
                    <h2>Welcome to Elite Sparkle!</h2>
                    <p>Thank you for registering. Please verify your email address to complete your registration.</p>
                    <div class="otp-code">{kwargs.get('otp', '000000')}</div>
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Elite Sparkle - Premium Jewelry Pakistan</p>
                    <p>Handcrafted with Love | Free Shipping Across Pakistan</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    elif template_name == 'password_reset':
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ ELITE SPARKLE ✨</h1>
                    <p>Luxury Jewelry Pakistan</p>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password. Use the OTP below to create a new password.</p>
                    <div class="otp-code">{kwargs.get('otp', '000000')}</div>
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Elite Sparkle - Premium Jewelry Pakistan</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    elif template_name == 'order_shipped':
        order = kwargs.get('order', {})
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ ELITE SPARKLE ✨</h1>
                    <p>Luxury Jewelry Pakistan</p>
                </div>
                <div class="content">
                    <h2>🎉 Your Order Has Been Shipped! 🎉</h2>
                    <p>Dear <strong>{order.get('first_name', 'Customer')}</strong>,</p>
                    <p>Great news! Your order has been shipped and is on its way to you.</p>
                    <div class="order-details">
                        <p><strong>📦 Order Number:</strong> {order.get('order_number', 'N/A')}</p>
                        <p><strong>📍 Shipping Address:</strong> {order.get('address', 'N/A')}, {order.get('city', 'N/A')}</p>
                        <p><strong>📅 Shipped Date:</strong> {order.get('updated_at', 'Today')}</p>
                    </div>
                    <p>You can track your order status in your account dashboard.</p>
                    <a href="{kwargs.get('site_url', '#')}/my_orders" class="button">Track Your Order →</a>
                </div>
                <div class="footer">
                    <p>© 2024 Elite Sparkle - Premium Jewelry Pakistan</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    elif template_name == 'order_delivered':
        order = kwargs.get('order', {})
        site_url = kwargs.get('site_url', '#')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ ELITE SPARKLE ✨</h1>
                    <p>Luxury Jewelry Pakistan</p>
                </div>
                <div class="content">
                    <h2>🎁 Your Order Has Been Delivered! 🎁</h2>
                    <p>Dear <strong>{order.get('first_name', 'Customer')}</strong>,</p>
                    <p>Your order has been successfully delivered. We hope you love your new jewelry!</p>
                    <div class="order-details">
                        <p><strong>📦 Order Number:</strong> {order.get('order_number', 'N/A')}</p>
                        <p><strong>📍 Delivered to:</strong> {order.get('address', 'N/A')}, {order.get('city', 'N/A')}</p>
                    </div>
                    <h3>⭐ We Value Your Feedback! ⭐</h3>
                    <p>Please take a moment to review your purchased items. Your feedback helps us improve and helps other customers make better choices.</p>
                    <a href="{site_url}/write_review/{order.get('id', 0)}" class="button">Write a Review →</a>
                </div>
                <div class="footer">
                    <p>© 2024 Elite Sparkle - Premium Jewelry Pakistan</p>
                    <p>Thank you for shopping with us!</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    elif template_name == 'review_request':
        order = kwargs.get('order', {})
        site_url = kwargs.get('site_url', '#')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ ELITE SPARKLE ✨</h1>
                    <p>Luxury Jewelry Pakistan</p>
                </div>
                <div class="content">
                    <h2>💎 Share Your Experience! 💎</h2>
                    <p>Dear <strong>{order.get('first_name', 'Customer')}</strong>,</p>
                    <p>We hope you're enjoying your recent purchase from Elite Sparkle!</p>
                    <p>Your opinion matters to us and to other jewelry lovers. Would you mind sharing your experience?</p>
                    <a href="{site_url}/write_review/{order.get('id', 0)}" class="button">Write a Review →</a>
                    <p style="margin-top: 20px;">It takes just a minute and helps us serve you better!</p>
                </div>
                <div class="footer">
                    <p>© 2024 Elite Sparkle - Premium Jewelry Pakistan</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    else:
        return "<html><body>Email template not found</body></html>"