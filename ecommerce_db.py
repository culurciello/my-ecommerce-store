import sqlite3
from sqlite3 import Error

import hashlib

class ecommerce_db:
    def __init__(self, filename):

        self.filename = filename
        self.connection = None
        self.cursor = None

        self.create_users_table = """CREATE TABLE IF NOT EXISTS users 
                (user_id INTEGER PRIMARY KEY, 
                password TEXT,
                email TEXT,
                first_name TEXT,
                last_name TEXT,
                address1 TEXT,
                address2 TEXT,
                zipcode TEXT,
                city TEXT,
                state TEXT,
                country TEXT, 
                phone TEXT
                )"""

        self.create_products_table = """CREATE TABLE IF NOT EXISTS products
                (product_id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                description TEXT,
                image TEXT,
                stock INTEGER,
                category_id INTEGER,
                FOREIGN KEY(category_id) REFERENCES categories(category_id)
                )"""

        self.create_ucart_table = """CREATE TABLE IF NOT EXISTS ucart
                (user_id INTEGER,
                product_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id)
                )"""

        self.create_categories_table = """CREATE TABLE IF NOT EXISTS categories
                (category_id INTEGER PRIMARY KEY,
                name TEXT
                )"""

        self.create_connection()
        self.execute_query(self.create_users_table)
        self.execute_query(self.create_products_table)
        self.execute_query(self.create_ucart_table)
        self.execute_query(self.create_categories_table)
        self.connection.close()


    def create_connection(self):
        try:
            self.connection = sqlite3.connect(self.filename)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.connection

    def execute_query(self, query, params=None):
        self.cursor = self.connection.cursor()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    def close_connection(self):
        self.connection.close()
        print("Connection closed!")