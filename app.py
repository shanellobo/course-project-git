from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime
import products

app = Flask(__name__)
app.secret_key = 'your_secret_key_123'

@app.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = {}
    # Convert product IDs to strings for JSON serialization
    session['cart'] = {str(k): v for k, v in session['cart'].items()}
    return render_template('index.html', products=products.products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        product_id = str(request.form['product_id'])  # Keep as string for session
        quantity = int(request.form['quantity'])
        
        # Validate product exists
        if not any(str(p['id']) == product_id for p in products.products):
            flash("Product not found!", "error")
            return redirect(url_for('index'))
        
        if quantity <= 0:
            flash("Invalid quantity!", "error")
            return redirect(url_for('index'))
        
        # Update cart
        if product_id in session['cart']:
            session['cart'][product_id] += quantity
        else:
            session['cart'][product_id] = quantity
        
        session.modified = True
        flash("Item has been added to the cart!", "success")  # Flash success message
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error adding to cart: {e}")
        flash("An error occurred while adding the item to the cart.", "error")
        return redirect(url_for('index'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        product_id = str(request.form['product_id'])
        if product_id in session['cart']:
            del session['cart'][product_id]
            session.modified = True
        return redirect(url_for('view_cart'))
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    try:
        cart_items = []
        total = 0
        
        for product_id, quantity in session.get('cart', {}).items():
            # Find product with string comparison
            product = next((p for p in products.products if str(p['id']) == product_id), None)
            if product:
                subtotal = product['price'] * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total += subtotal
        
        return render_template('cart.html', cart_items=cart_items, total=total)
    except Exception as e:
        print(f"Error viewing cart: {e}")
        return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('cart'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        session['customer_info'] = {
            'name': request.form['name'],
            'email': request.form['email'],
            'address': request.form['address']
        }
        return redirect(url_for('generate_bill'))
    
    return render_template('checkout.html')

@app.route('/bill')
def generate_bill():
    try:
        if not session.get('cart') or not session.get('customer_info'):
            return redirect(url_for('index'))
        
        cart_items = []
        total = 0
        
        for product_id, quantity in session.get('cart', {}).items():
            product = next((p for p in products.products if str(p['id']) == product_id), None)
            if product:
                subtotal = product['price'] * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total += subtotal
        
        # Clear cart after generating bill
        session.pop('cart', None)
        
        return render_template('bill.html',
            cart_items=cart_items,
            total=total,
            customer_info=session['customer_info'],
            date=datetime.now().strftime("%B %d, %Y %H:%M:%S")
        )
    except Exception as e:
        print(f"Error generating bill: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)