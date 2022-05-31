# import sqlite3
# from sqlite3 import Error
import sqlalchemy as db

import hashlib

class ecommerce_db:
    def __init__(self, filename):

        self.filename = filename
        # self.connection = None
        # self.cursor = None

        self.engine = db.create_engine(filename, echo=True)
        self.metadata_obj = db.MetaData()

        # create tables;
        self.users = db.Table(
            'users',
            self.metadata_obj,
            db.Column('user_id', db.String, primary_key=True),  
            db.Column('password', db.String),                    
            db.Column('email', db.String), 
            db.Column('first_name', db.String),
            db.Column('last_name', db.String),
            db.Column('address1', db.String),
            db.Column('address2', db.String),
            db.Column('zipcode', db.Integer),
            db.Column('city', db.String),
            db.Column('state', db.String),
            db.Column('country', db.String),
            db.Column('phone', db.Integer),
        )

        self.products = db.Table(
            'products',
            self.metadata_obj,
            db.Column('product_id', db.Integer, primary_key=True),
            db.Column('name', db.String),
            db.Column('price', db.Float),
            db.Column('description', db.String),
            db.Column('image', db.String),
            db.Column('stock', db.Integer),
            db.Column('category_id', db.Integer, db.ForeignKey("categories.category_id"), nullable=False),
        )

        self.cart = db.Table(
            'cart',
            self.metadata_obj,
            db.Column('user_id', db.Integer),
            db.Column('product_id', db.Integer),
            db.Column('user_id', db.Integer, db.ForeignKey("users.user_id"), nullable=False),
            db.Column('product_id', db.Integer, db.ForeignKey("products.product_id"), nullable=False),
        )

        self.categories = db.Table(
            'categories',
            self.metadata_obj,
            db.Column('category_id', db.Integer, primary_key=True),
            db.Column('name', db.String),
        )
          
        # create the tables:
        self.metadata_obj.create_all(self.engine)

        # self.create_users_table = """CREATE TABLE IF NOT EXISTS users 
        #         (user_id INTEGER PRIMARY KEY, 
        #         password TEXT,
        #         email TEXT,
        #         first_name TEXT,
        #         last_name TEXT,
        #         address1 TEXT,
        #         address2 TEXT,
        #         zipcode TEXT,
        #         city TEXT,
        #         state TEXT,
        #         country TEXT, 
        #         phone TEXT
        #         )"""

        # self.create_products_table = """CREATE TABLE IF NOT EXISTS products
        #         (product_id INTEGER PRIMARY KEY,
        #         name TEXT,
        #         price REAL,
        #         description TEXT,
        #         image TEXT,
        #         stock INTEGER,
        #         category_id INTEGER,
        #         FOREIGN KEY(category_id) REFERENCES categories(category_id)
        #         )"""

        # self.create_cart_table = """CREATE TABLE IF NOT EXISTS cart
        #         (user_id INTEGER,
        #         product_id INTEGER,
        #         FOREIGN KEY(user_id) REFERENCES users(user_id),
        #         FOREIGN KEY(product_id) REFERENCES products(product_id)
        #         )"""

        # self.create_categories_table = """CREATE TABLE IF NOT EXISTS categories
        #         (category_id INTEGER PRIMARY KEY,
        #         name TEXT
        #         )"""

        # self.create_connection()
        # self.execute_query(self.create_users_table)
        # self.execute_query(self.create_products_table)
        # self.execute_query(self.create_cart_table)
        # self.execute_query(self.create_categories_table)
        # self.connection.close()


    # def create_connection(self):
    #     try:
    #         self.connection = sqlite3.connect(self.filename)
    #         print("Connection to SQLite DB successful")
    #     except Error as e:
    #         print(f"The error '{e}' occurred")

    #     return self.connection

    # def execute_query(self, query, params=None):
    #     # print("Query, params:", query, params)
    #     self.cursor = self.connection.cursor()
    #     try:
    #         if params:
    #             self.cursor.execute(query, params)
    #         else:
    #             self.cursor.execute(query)

    #         self.connection.commit()
    #         print("Query executed successfully")
    #     except Error as e:
    #         print(f"The error '{e}' occurred")

    # def close_connection(self):
    #     self.connection.close()
    #     print("Connection closed!")