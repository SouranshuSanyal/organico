from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, make_response
from flask_login import login_required, current_user
import pdfkit
import json
from . import db, mail
from .models import User, Products, Cart, CartItem, Address, Order, OrderItem
from .utils import admin_required
import json
from datetime import datetime
from flask_mail import Message


views = Blueprint('views', __name__)


@views.route('/')
def home():
    items = Products.query.all()
    return render_template('home.html', items = items)


@views.route('/fruits')
def fruitlist():
    fruits = Products.query.filter_by(category='fruits').all()
    return render_template('fruits.html', fruits=fruits)


@views.route('/vegetables')
def vegetablelist():
    vegetables = Products.query.filter_by(category='vegetables').all()
    return render_template('vegetables.html', vegetables=vegetables)


@views.route('/flowers')
def flowerlist():
    flowers = Products.query.filter_by(category='flowers').all()
    return render_template('flowers.html', flowers=flowers)


@views.route('/cart')
@login_required
def cart():
    user_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not user_cart:
        # This user has no cart yet.
        flash('Your cart is empty.', category='info')
        return render_template('cart.html', cartitems=[], total_price=0)
    cartitems = CartItem.query.filter_by(cart_id=user_cart.id).all()
    total_price = sum(item.total_price for item in cartitems)
    return render_template('cart.html', cartitems=cartitems, total_price=total_price)


@views.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):

    data = request.json
    quantity = data.get('quantity')

    # Get the product from the database.
    product = Products.query.get(product_id)
    if not product:
        flash('Product not found!', category='error')
        return redirect(url_for('views.home'))

    # Get the cart of the current user, create one if it doesn't exist.
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
        flash("Item added to cart", category='success')

        # Check if the product is already in the cart.
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:

        cart_item.quantity += int(quantity)
        flash("Item added to cart", category='success')

    else:

        cart_item = CartItem(product_id=product_id,
                             cart_id=cart.id, quantity=quantity)
        db.session.add(cart_item)
        flash("Item added to cart", category='success')
    db.session.commit()
    
    return jsonify(success=True, message="Product added/updated in cart")
    

@views.route('/edit_quantity/<int:cartitem_id>', methods=['GET', 'POST'])
@login_required
def edit_quantity(cartitem_id):
    cartitem = CartItem.query.get_or_404(cartitem_id)
    if request.method == 'POST':
        cartitem.quantity = request.form.get('quantity')
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('views.cart'))

    return render_template('edit_quantity.html', cartitem=cartitem)


@views.route('/remove_from_cart/<int:cartitem_id>')
@login_required
def remove_from_cart(cartitem_id):
    remove_cart = CartItem.query.get_or_404(cartitem_id)
    db.session.delete(remove_cart)
    db.session.commit()
    flash('Product removed from cart!', 'success')
    return redirect(url_for('views.cart'))


@views.route('/admindashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admindashboard():
    return render_template('admindashboard.html')


@views.route('/productlist')
@login_required
@admin_required
def viewproduct():
    products = Products.query.all()
    return render_template('productlist.html', products=products)

@views.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)
    if request.method == 'POST':
        product.productPrice = request.form.get('productPrice')
        product.stock = request.form.get('stock')
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('views.viewproduct'))

    return render_template('edit_product.html', product=product)


@views.route('/delete_product/<int:product_id>')
@login_required
@admin_required
def deleteproduct(product_id):
    delete_product = Products.query.get_or_404(product_id)
    db.session.delete(delete_product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('views.viewproduct'))


@views.route('/userlist')
@login_required
@admin_required
def userlist():
    users = User.query.all()
    return render_template('userlist.html', users=users)


@views.route('/delete-user', methods=['POST'])
def deleteUser():

    data = request.json

    userid = data.get('userid')

    if not userid:
        return jsonify({"error": "No user ID provided"}), 400

    user = User.query.get(userid)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User Deleted Successfully', category='success')
        return jsonify({"message": "User deleted successfully"})

    return jsonify({"error": "User not found"}), 404




@views.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Get address details from the form
        address_line1 = request.form.get('address_line1')
        address_line2 = request.form.get('address_line2')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        
        # Save the address
        address = Address(user_id=current_user.id, address_line1=address_line1, address_line2=address_line2,
                          city=city, state=state, postal_code=postal_code, country=country)
        db.session.add(address)
        db.session.commit()

        # Generate a unique order ID (You can format this in any way you prefer)
        order_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + str(current_user.id)
        
        # Save the order
        order = Order(order_id=order_id, user_id=current_user.id, address_id=address.id)
        
        db.session.add(order)
        db.session.commit()
        

        user_cart = Cart.query.filter_by(user_id=current_user.id).first()
        # Before processing the order, let's check stock availability
        for cartitem in user_cart.items:
            product = cartitem.product
            new_stock = int(product.stock) - cartitem.quantity

            # Check for insufficient stock
            if new_stock < 0:
                flash(f"Sorry, we don't have enough stock for {product.productName}. Please reduce the quantity to {product.stock} or remove the item from your cart.", 'error')
                return redirect(url_for('views.cart'))

        # If stock is sufficient, proceed with order processing and stock reduction
        for cartitem in user_cart.items:
            product = cartitem.product
            product.stock = str(int(product.stock) - cartitem.quantity)  # Reduce stock
            db.session.add(product)
        
        
        for item in user_cart.items:
            order_item = OrderItem(product_id=item.product_id, order_id=order.id, quantity=item.quantity)
            db.session.add(order_item)
            db.session.delete(item)  # Optional: remove the cart item if you decide to do so
        
        db.session.commit()
        flash('Order placed successfully!', 'success')

        # Redirect to a confirmation page or order details page
        return redirect(url_for('views.order_details', order_id=order.id))
    
    return render_template('checkout.html')

@views.route('/order_details/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash('Access restricted!', 'error')
        return redirect(url_for('views.home'))
    
    cart_items = CartItem.query.filter_by(order_id=order.id).all()
    print("Cart items associated with order:", len(cart_items))

    return render_template('order_details.html', order=order)


@views.route('/myorders')
@login_required
def myorders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    if not user_orders:
        flash('Your have no  orders.', category='info')
        return render_template('myorders.html', myorders=[])
    
    order_ids = [order.id for order in user_orders]
    myorders = OrderItem.query.filter(OrderItem.order_id.in_(order_ids)).all()
    
    return render_template('myorders.html', myorders=myorders)

@views.route('/delete_order/<int:order_id>')
@login_required
def deleteorder(order_id):
    delete_order = Order.query.get_or_404(order_id)
    db.session.delete(delete_order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('views.myorders'))




@views.route('/download_bill/<int:order_id>')
@login_required
def download_bill(order_id):
    # Fetch order details using order_id
    order = Order.query.get_or_404(order_id)

    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        abort(403)  # Forbidden

    # Render an HTML template with the order details
    rendered = render_template('bill_template.html', order=order, current_user = current_user)
    
    # Convert the HTML to a PDF
    try:
        pdf = pdfkit.from_string(rendered, False)
    except Exception as e:
        return str(e)

    # Create a response to send the PDF back
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=bill_{order_id}.pdf'
    
    return response

@views.route('/send_email/<int:order_id>')
def send_email(order_id):
    order = Order.query.get_or_404(order_id)
    user = User.query.get(order.user_id)
    
    # Ensure there's a user associated with the order.
    if not user:
        flash('Error: User associated with the order not found.', 'error')
        return redirect(url_for('views.myorders'))

    # Generate the PDF from the template
    html_string = render_template('bill_template.html', order=order)
    pdf_bytes = pdfkit.from_string(html_string, False)

    # Setup the email
    msg = Message('Order Confirmation', sender='souranshus@gmail.com', recipients=[user.email])
    msg.body = 'Thank you for your order!'
    msg.attach("order.pdf", "application/pdf", pdf_bytes)
    
    mail.send(msg)
    
    flash('Mail Sent', category = 'success')
    return redirect(url_for('views.myorders'))


























@views.route('/testpdf')
def testpdf():
    rendered = render_template('test_template.html')
    try:
        pdf = pdfkit.from_string(rendered, False)
    except Exception as e:
        return str(e)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=test.pdf'
    return response



