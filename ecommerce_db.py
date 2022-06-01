import os
import json
import sqlalchemy as db

class ecommerce_db:
    def __init__(self, filename):
        self.filename = filename

        self.engine = db.create_engine(filename, echo=True)
        self.metadata_obj = db.MetaData()


    def create_tables(self):
        # create tables;
        self.users = db.Table(
            'users',
            self.metadata_obj,
            db.Column('user_id', db.Integer, primary_key=True),  
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

    def add_dataset_to_store(self, rootdir):
        # categories = []

        # db acces:
        connection = self.engine.connect()

        for category in os.listdir(rootdir):
            cat_dir = os.path.join(rootdir, category)
            
            if os.path.isdir(cat_dir):
                # print(category) # categories in store
                # categories.append(category)
                # insert category into db:
                try:
                    query = db.insert(self.categories).values(name=category)
                    connection.execute(query)
                    message = "Added category to store successfully"
                except:
                    connection.rollback()
                    message = "Error occured!"

                # get category id number:
                query = self.categories.select().where(self.categories.columns.name == category)
                category_num = connection.execute(query).fetchone()[0]
                # print("===> category num:", category_num)

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
                            query = db.insert(self.products).values(
                                name=name,
                                price=price,
                                description=description,
                                image=imagename,
                                stock=stock,
                                category_id=category_id)
                            connection.execute(query)
                            message = "Added item to store successfully"
                        except:
                            # connection.rollback()
                            message = "Error occured!"

                        print(message)

        connection.close()