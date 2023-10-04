from flask import Blueprint, render_template, request, flash, redirect, url_for
from.models import User, Products
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .utils import admin_required

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')
        
        user = User.query.filter_by(phoneNumber = phoneNumber).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in Successfully", category= 'success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password', category='error')  
                
        else:
            flash('Phone Number does not exists', category='error')      
    return render_template('login.html')





@auth.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out', category='success')
    return redirect(url_for('views.home'))







@auth.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')
        cnfpassword = request.form.get('cnfpassword')
        
        user = User.query.filter_by(phoneNumber=phoneNumber).first()
        useremail = User.query.filter_by(email=email).first()
        if user:
            flash('Phone number already exists', category='error')
        elif useremail:
            flash('Email already exists', category='error')
        elif len(name) < 1:
            flash('Name is required', category='error')
        elif len(phoneNumber) < 1:
            flash('Phone Number is required', category='error')
        elif password != cnfpassword:
            flash('Paswords do not match', category='error')
        elif len(password) < 7:
                flash('Password must be greater than 6 characters.', category='error')
        else:
            new_user = User(phoneNumber = phoneNumber, email=email, name=name, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account Created", category= 'success')
            return redirect(url_for('views.home'))
    
    return render_template('signup.html')







@auth.route('/adminsignup', methods = ['GET', 'POST'])
def adminsignup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')
        cnfpassword = request.form.get('cnfpassword')
        verificationcode = request.form.get('verificationcode')
        
        user = User.query.filter_by(phoneNumber=phoneNumber).first()
        useremail= User.query.filter_by(email = email).first()
        
        if user:
            flash('Phone Number Already Exits', category= 'error')
        elif useremail:
            flash('Email Already Exits', category= 'error')
        else:        
            if len(name) < 1:
                flash('Name is required', category='error')
            elif len(phoneNumber) < 1:
                flash('Phone Number is required', category='error')
            elif password != cnfpassword:
                flash('Paswords do not match', category='error')
            elif len(password) < 7:
                    flash('Password must be greater than 6 characters.', category='error')
            elif (verificationcode != '56789'):
                    flash('Verification Code does not match', category='error')
            else:
                new_admin = User(phoneNumber = phoneNumber, email=email, name=name, password=generate_password_hash(password, method='sha256'), role = 'admin')
                db.session.add(new_admin)
                db.session.commit()
                login_user(new_admin, remember=True)
                flash("Account Created", category= 'success')
                return redirect(url_for('views.home'))
    
    return render_template('adminsignup.html')

@auth.route('/addproduct', methods = ['GET', 'POST'])
@login_required
@admin_required
def productlist():
    if request.method == 'POST':
        productID = request.form.get('productID')
        productName = request.form.get('productName')
        productPrice = request.form.get('price')
        category = request.form.get('category')
        stock = request.form.get('stock')
        
        product = Products.query.filter_by(productID = productID).first()
        
        if product:
            flash("Product ID already exists", category='error')
        elif not productName or len(productName)<1:
                flash('Please Enter the Product Name', category='error')
        else:
            new_product = Products(productID = productID, productName = productName, productPrice = productPrice, category=category, stock = stock)
            db.session.add(new_product)
            db.session.commit()
            flash('Product Added', category = 'success')
            return redirect(url_for('views.admindashboard'))
            
        
        
    return render_template('addproduct.html')


