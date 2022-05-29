# e-commerce store template
# E. Culurciello, May 2022

# inspired by: https://github.com/HarshShah1997/Shopping-Cart

from flask import *
from ecommerce_db import ecommerce_db
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
my_ecommerce_db_filename = "my_ecommerce.db"
app.secret_key = 'my ecommerce store'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# my database:
my_ecommerce_db = ecommerce_db(my_ecommerce_db_filename)

def get_login_info():
    with my_ecommerce_db.create_connection():
        if 'email' not in session:
            logged_in = False
            first_name = ''
            num_items = 0
        else:
            logged_in = True
            q = "SELECT user_id, first_name FROM users WHERE email = ?"
            my_ecommerce_db.execute_query(q, (session['email'], ))
            user_id, first_name = my_ecommerce_db.cursor.fetchone()
            q = "SELECT count(product_id) FROM cart WHERE user_id = ?"
            my_ecommerce_db.execute_query(q, (user_id, ))
            num_items = my_ecommerce_db.cursor.fetchone()[0]

    my_ecommerce_db.close_connection()

    return (logged_in, first_name, num_items)


def is_valid(email, password):
    my_ecommerce_db.create_connection()
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
    my_ecommerce_db.create_connection()

    q = "SELECT product_id, name, price, description, image, stock FROM products"
    my_ecommerce_db.execute_query(q)
    item_data = my_ecommerce_db.cursor.fetchall()

    q = "SELECT category_id, name FROM categories"
    my_ecommerce_db.execute_query(q)
    category_data = my_ecommerce_db.cursor.fetchall()

    my_ecommerce_db.close_connection()

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
            msg = "Registration Successfully"
        except:
            my_ecommerce_db.connection.rollback()
            msg = "Registration Error!"

        my_ecommerce_db.close_connection()

        return render_template("login.html", message=msg)


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
            msg = "Registration edit Successfully"
        except:
            my_ecommerce_db.connection.rollback()
            msg = "Registration edit Error!"

        my_ecommerce_db.close_connection()

        logged_in, first_name, num_items = get_login_info()

        return render_template("profile_home.html", logged_in=logged_in, first_name=first_name, num_items=num_items)


@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('login_form'))

    logged_in, first_name, num_items = get_login_info()
    email = session['email']

    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT user_id FROM users WHERE email = ?"
    params = (email, )
    my_ecommerce_db.execute_query(q, params)
    user_id = my_ecommerce_db.cursor.fetchone()[0]

    q = "SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?"
    params = (user_id, )
    my_ecommerce_db.execute_query(q, params)
    products = my_ecommerce_db.cursor.fetchall()
    total_price = 0
    for row in products:
        total_price += row[2]

    my_ecommerce_db.close_connection()

    return render_template("cart.html", products = products, totalPrice=total_price, logged_in=logged_in, firstName=first_name, noOfItems=num_items)



@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('login_form'))
    else:
        product_id = int(request.args.get('product_id'))

        # db acces:
        my_ecommerce_db.create_connection()
        q = "SELECT user_id FROM users WHERE email = ?"
        my_ecommerce_db.execute_query(q, params)
        user_id = my_ecommerce_db.cursor.fetchone()[0]

        try:
            q = "INSERT INTO cart (user_id, product_id) VALUES (?, ?)"
            params = (user_id, product_id)
            my_ecommerce_db.execute_query(q, params)
            message = "Added to cart successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured!"

        my_ecommerce_db.close_connection()

        return redirect(url_for('root'))


@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('login_form'))

    email = session['email']
    product_id = int(request.args.get('product_id'))
    
    # db acces:
    my_ecommerce_db.create_connection()
    q = "SELECT user_id FROM users WHERE email = ?"
    params = (email, )
    user_id = my_ecommerce_db.cursor.fetchone()[0]

        try:
            q = "DELETE FROM cart WHERE user_id = ? AND product_id = ?"
            params = (user_id, product_id)
            my_ecommerce_db.execute_query(q, params)
            message = "Removed from cart successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured!"
    
    my_ecommerce_db.close_connection()

    return redirect(url_for('root'))



if __name__ == '__main__':
    app.run(debug=True)