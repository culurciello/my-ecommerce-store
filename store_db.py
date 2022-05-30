# populate store items database

import os
import json
from ecommerce_db import ecommerce_db

# my database:
my_ecommerce_db_filename = "my_ecommerce.db"
my_ecommerce_db = ecommerce_db(my_ecommerce_db_filename)

# items directory:
rootdir = 'static/store_items/'

# categories = []
category_num = 0

# db acces:
my_ecommerce_db.create_connection()

for category in os.listdir(rootdir):
    cat_dir = os.path.join(rootdir, category)
    
    if os.path.isdir(cat_dir):
        # print(category) # categories in store
        # categories.append(category)
        category_num += 1
        # insert category into db:
        try:
            q = "INSERT INTO categories (category_id, name) VALUES (?, ?)"
            params = (category_num, category)
            my_ecommerce_db.execute_query(q, params)
            message = "Added category to store successfully"
        except:
            my_ecommerce_db.connection.rollback()
            message = "Error occured!"

        for item in os.listdir(cat_dir):
            item_dir = os.path.join(cat_dir, item)
            if os.path.isdir(item_dir):
                print(category, ':\t', item) # items in category
                datafile = os.path.join(item_dir, "data.txt")
                imagefile = os.path.join(item_dir, "image.jpg")
                # print(datafile, imagefile)
                f = open(datafile)
                data = json.load(f)

                # load data from files:
                name = data["name"]
                price = float(data["price"])
                description = data["description"]
                stock = int(data["stock"])
                category_id = category_num
                imagename = imagefile

                # insert item into db:
                try:
                    q = "INSERT INTO products (name, price, description, image, stock, category_id) VALUES (?, ?, ?, ?, ?, ?)"
                    params = (name, price, description, imagename, stock, category_id)
                    my_ecommerce_db.execute_query(q, params)
                    message = "Added item to store successfully"
                except:
                    my_ecommerce_db.connection.rollback()
                    message = "Error occured!"

                print(message)

my_ecommerce_db.close_connection()
# print('categories', categories)
