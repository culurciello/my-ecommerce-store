# populate store items database

import os
import json
import sqlalchemy as db
from ecommerce_db import ecommerce_db

# my database:
my_ecommerce_db_filename = "sqlite:///my_ecommerce.db"
my_ecommerce_db = ecommerce_db(my_ecommerce_db_filename)
my_ecommerce_db.create() # creates all table!

# items directory:
rootdir = 'static/store_items/'

# categories = []
category_num = 0

# db acces:
connection = my_ecommerce_db.engine.connect()

for category in os.listdir(rootdir):
    cat_dir = os.path.join(rootdir, category)
    
    if os.path.isdir(cat_dir):
        # print(category) # categories in store
        # categories.append(category)
        category_num += 1
        # insert category into db:
        try:
            query = db.insert(my_ecommerce_db.categories).values(category_id=category_num, name=category)
            connection.execute(query)
            message = "Added category to store successfully"
        except:
            connection.rollback()
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
                    query = db.insert(my_ecommerce_db.products).values(
                        name=name,
                        price=price,
                        description=description,
                        image=imagename,
                        stock=stock,
                        category_id=category_id)
                    connection.execute(query)
                    message = "Added item to store successfully"
                except:
                    connection.rollback()
                    message = "Error occured!"

                print(message)

connection.close()
# print('categories', categories)
