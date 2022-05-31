# e-commerce store template
# E. Culurciello, May 2022

import os
# import sqlite3
import sqlalchemy as db
import hashlib
from werkzeug.utils import secure_filename
from flask import *
from ecommerce_db import ecommerce_db

app = Flask(__name__)
my_ecommerce_db_filename = "sqlite:///my_ecommerce.db"
app.secret_key = 'my ecommerce store'
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# session.clear() # clear the old session if any!

# my database:
my_ecommerce_db = ecommerce_db(my_ecommerce_db_filename)

def get_login_info():
    # with my_ecommerce_db.create_connection():
    connection = my_ecommerce_db.engine.connect()
    if 'email' not in session:
        logged_in = False
        first_name = ''
        num_items = 0
    else:
        logged_in = True
        query = db.select(
            [my_ecommerce_db.users.columns.user_id, 
             my_ecommerce_db.users.columns.first_name]
        ).where(my_ecommerce_db.users.columns.email == session['email'])

        r = connection.execute(query).fetchone()
        print(r)
        crap

        #q = "SELECT user_id, first_name FROM users WHERE email = ?"
        #my_ecommerce_db.execute_query(q, (session['email'], ))
        #user_id, first_name = my_ecommerce_db.cursor.fetchone()
        #q = "SELECT count(product_id) FROM cart WHERE user_id = ?"
        #my_ecommerce_db.execute_query(q, (user_id, ))
        #num_items = my_ecommerce_db.cursor.fetchone()[0]

    # my_ecommerce_db.close_connection()

    return (logged_in, first_name, num_items)


def is_valid(email, password):
    # my_ecommerce_db.create_connection()
    connection = my_ecommerce_db.engine.connect()
    q = "SELECT email, password FROM users"
    my_ecommerce_db.execute_query(q)
    data = my_ecommerce_db.cursor.fetchall()
    my_ecommerce_db.close_connection()
    
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    
    return False


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    
    return ans


# app routes:
@app.route("/")
def root():
    logged_in, first_name, num_items = get_login_info()
    # my_ecommerce_db.create_connection()
    connection = my_ecommerce_db.engine.connect()
    query = db.select(
            [my_ecommerce_db.products.columns.product_id,
             my_ecommerce_db.products.columns.name,
             my_ecommerce_db.products.columns.price,
             my_ecommerce_db.products.columns.description,
             my_ecommerce_db.products.columns.image,
             my_ecommerce_db.products.columns.stock]
        )
    item_data = connection.execute(query).fetchall()
    # q = "SELECT product_id, name, price, description, image, stock FROM products"
    # my_ecommerce_db.execute_query(q)
    # item_data = my_ecommerce_db.cursor.fetchall()

    query = db.select(
            [my_ecommerce_db.categories.columns.category_id,
             my_ecommerce_db.categories.columns.name]
        )
    category_data = connection.execute(query).fetchall()
    # q = "SELECT category_id, name FROM categories"
    # my_ecommerce_db.execute_query(q)
    # category_data = my_ecommerce_db.cursor.fetchall()

    # my_ecommerce_db.close_connection()
    connection.close()

    item_data = parse(item_data)   
    
    return render_template("home.html", item_data=item_data, logged_in=logged_in, first_name=first_name, num_items=num_items, category_data=category_data)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        # db acces:
        my_ecommerce_db.create_connection()
        try:
            q = "INSERT INTO users (password, email, first_name, last_name, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (hashlib.md5(password.encode()).hexdigest(), email, first_name, last_name, address1, address2, zipcode, city, state, country, phone)
            my_ecommerce_db.execute_query(q, params)
            message = "Registration Successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Registration Error!"

        my_ecommerce_db.close_connection()

        return render_template("login.html", message=message)


@app.route("/registration_form")
def registration_form():
    return render_template("register.html")


@app.route("/login_form")
def login_form():
    if 'email' in session:
        return redirect(url_for("root"))
    else:
        return render_template("login.html", message="")


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            message = "Invalid User ID / Password!"
            return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


@app.route("/account/profile")
def profile_home():
    if 'email' not in session:
        return redirect(url_for('root'))
    logged_in, first_name, num_items = get_login_info()

    return render_template("profile_home.html", logged_in=logged_in, first_name=first_name, num_items=num_items)


@app.route("/account/profile/edit")
def profile_edit():
    if 'email' not in session:
        return redirect(url_for('root'))

    logged_in, first_name, num_items = get_login_info()

    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT user_id, email, first_name, last_name, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?"
    params = (session['email'], )
    my_ecommerce_db.execute_query(q, params)
    profile_data = my_ecommerce_db.cursor.fetchone()
    my_ecommerce_db.close_connection()

    return render_template("profile_edit.html", profile_data=profile_data, logged_in=logged_in, first_name=first_name, num_items=num_items)


@app.route("/account/profile/password_change", methods=["GET", "POST"])
def password_change():
    if 'email' not in session:
        return redirect(url_for('login_form'))
    if request.method == "POST":
        old_password = request.form['oldpassword']
        old_password = hashlib.md5(old_password.encode()).hexdigest()
        new_password = request.form['newpassword']
        new_password = hashlib.md5(new_password.encode()).hexdigest()

        my_ecommerce_db.create_connection()
        q = "SELECT user_id, password FROM users WHERE email = ?"
        params = (session['email'], )
        my_ecommerce_db.execute_query(q, params)
        user_id, password = my_ecommerce_db.cursor.fetchone()
        if (password == old_password):
            try:
                q = "UPDATE users SET password = ? WHERE user_id = ?"
                params = (new_password, user_id)
                my_ecommerce_db.execute_query(q, params)
                message = "Changed successfully"
            except:
                my_ecommerce_db.connection.rollback()
                message = "Failed"
            return render_template("password_change.html", message=message)
        else:
            message = "Wrong password"

        my_ecommerce_db.close_connection()
        
        return render_template("password_change.html", message=message)
    else:
        return render_template("password_change.html")


@app.route("/account/orders")
def account_orders():
    # TBD
    message = "Not implemented yet!"
    return render_template('account_orders.html', message=message)


@app.route("/profile_update", methods=["GET", "POST"])
def profile_update():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        # db acces:
        my_ecommerce_db.create_connection()
        try:
            q = "UPDATE users SET first_name = ?, last_name = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?"
            params = (first_name, last_name, address1, address2, zipcode, city, state, country, phone, email)
            my_ecommerce_db.execute_query(q, params)
            message = "Registration edit Successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Registration edit Error!"

        my_ecommerce_db.close_connection()

        logged_in, first_name, num_items = get_login_info()

        return render_template("profile_home.html", logged_in=logged_in, first_name=first_name, num_items=num_items)



@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('login_form'))
    else:
        logged_in, first_name, num_items = get_login_info()
        email = session['email']

        # db acces:
        my_ecommerce_db.create_connection()
        q = "SELECT user_id FROM users WHERE email = ?"
        params = (email, )
        my_ecommerce_db.execute_query(q, params)
        user_id = my_ecommerce_db.cursor.fetchone()[0]

        q = "SELECT products.product_id, products.name, products.price, products.image FROM products, cart WHERE products.product_id = cart.product_id AND cart.user_id = ?"
        params = (user_id, )
        my_ecommerce_db.execute_query(q, params)
        products = my_ecommerce_db.cursor.fetchall()
        total_price = 0
        for row in products:
            total_price += row[2]

        my_ecommerce_db.close_connection()

        return render_template("cart.html", products = products, total_price=total_price, logged_in=logged_in, first_name=first_name, num_items=num_items)



@app.route("/add_to_cart")
def add_to_cart():
    if 'email' not in session:
        return redirect(url_for('login_form'))
    else:
        product_id = int(request.args.get('product_id'))

        # db acces:
        my_ecommerce_db.create_connection()
        q = "SELECT user_id FROM users WHERE email = ?"
        params = (session['email'], )
        my_ecommerce_db.execute_query(q, params)
        user_id = my_ecommerce_db.cursor.fetchone()[0]

        try:
            q = "INSERT INTO cart (user_id, product_id) VALUES (?, ?)"
            params = (user_id, product_id)
            my_ecommerce_db.execute_query(q, params)
            message = "Added to cart successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured while adding to cart!"

        my_ecommerce_db.close_connection()

        return redirect(url_for('root'))


@app.route("/remove_from_cart")
def remove_from_cart():
    if 'email' not in session:
        return redirect(url_for('login_form'))
    else:
        product_id = int(request.args.get('product_id'))
        
        # db acces:
        my_ecommerce_db.create_connection()
        q = "SELECT user_id FROM users WHERE email = ?"
        params = (session['email'], )
        my_ecommerce_db.execute_query(q, params)
        user_id = my_ecommerce_db.cursor.fetchone()[0]

        try:
            q = "DELETE FROM cart WHERE user_id = ? AND product_id = ?"
            params = (user_id, product_id)
            my_ecommerce_db.execute_query(q, params)
            message = "Removed from cart successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured while removing from cart!"
        
        my_ecommerce_db.close_connection()

        return redirect(url_for('root'))


@app.route("/product_description")
def product_description():
    logged_in, first_name, num_items = get_login_info()
    product_id = request.args.get('product_id')

    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT product_id, name, price, description, image, stock FROM products WHERE product_id = ?"
    params = (product_id, )
    my_ecommerce_db.execute_query(q, params)
    product_data = my_ecommerce_db.cursor.fetchone()
    my_ecommerce_db.close_connection()

    return render_template("product_description.html", data=product_data, loggedIn=logged_in, first_name=first_name, num_items=num_items)


# add items to store:
@app.route("/add_to_store")
def admin():
    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT category_id, name FROM categories"
    my_ecommerce_db.execute_query(q)
    categories = my_ecommerce_db.cursor.fetchall()
    my_ecommerce_db.close_connection()

    return render_template('store_add.html', categories=categories)


@app.route("/add_item_to_store", methods=["GET", "POST"])
def add_item_to_store():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        category_id = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename

        # db acces:
        my_ecommerce_db.create_connection()
        try:
            q = "INSERT INTO products (name, price, description, image, stock, category_id) VALUES (?, ?, ?, ?, ?, ?)"
            params = (name, price, description, imagename, stock, category_id)
            my_ecommerce_db.execute_query(q, params)
            message = "Added item to store successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured while adding item to store!"
            
        my_ecommerce_db.close_connection()

        print(mesage)
        
        return redirect(url_for('root'))



@app.route("/remove_from_store")
def remove_from_store():
    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT product_id, name, price, description, image, stock FROM products"
    my_ecommerce_db.execute_query(q)
    data = my_ecommerce_db.cursor.fetchall()
    my_ecommerce_db.close_connection()

    return render_template('store_remove.html', data=data)


@app.route("/remove_item_from_store")
def remove_item_from_store():
    product_id = request.args.get('product_id')

    # db acces:
    my_ecommerce_db.create_connection()
    try:
        q = "DELETE FROM products WHERE product_id = ?"
        params = (product_id, )
        my_ecommerce_db.execute_query(q, params)
        message = "Store item deleted successsfully"
    except:
        my_ecommerce_db.connection.rollback()
        message = "Error occured while deleting item from store!"

    my_ecommerce_db.close_connection()

    print(message)
    
    return redirect(url_for('root'))


@app.route("/category_display")
def category_display():
        logged_in, first_name, num_items = get_login_info()
        category_id = request.args.get("category_id")
        
        # db acces:
        my_ecommerce_db.create_connection()
        q = "SELECT products.product_id, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.category_id = categories.category_id AND categories.category_id = ?"
        params = (category_id, )
        my_ecommerce_db.execute_query(q, params)
        data = my_ecommerce_db.cursor.fetchall()
        my_ecommerce_db.close_connection()
        
        category_name = data[0][4]
        data = parse(data)
        
        return render_template('category_display.html', data=data, loggedIn=logged_in, firstName=first_name, num_items=num_items, category_name=category_name)


@app.route("/checkout")
def checkout():
    # TBD
    message = "Not implemented yet!"
    return render_template('checkout.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)