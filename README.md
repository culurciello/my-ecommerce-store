# my-ecommerce-store
 
An e-commerce website with users, items, shopping cart, etc. based on python and Flask.

You can create user profiles, change profiles, add and remove items to store, add and remove items to user cart.


## Store items:

Using a simple dataset of store items in `static/store_items`. The dataset format is as follows:


```
Category1/
		item11/
				data.txt
				image.txt
Category2/ 
		item21/
				data.txt
				image.txt
```

the data in `data.txt` is a JSON as follows:

```
{ 
  "name":"Wave t-shirt",
  "price":10.0,
  "description":"a t-shirt with a wave on it",
  "stock":5
}
```



## Run:

Before serving, you initialize the store database from `static/store_items`. Or you can add / remove items online with: `http://127.0.0.1:5000/add_to_store` or `http://127.0.0.1:5000/remove_from_store` (clock on items to remove them from the store).

Initialize store items into database:

```
python store_db.py
```


Web serving:

```
python app.py
```


###### References:

- https://www.tutorialspoint.com/sqlite/sqlite_python.htm
- https://github.com/HarshShah1997/Shopping-Cart
- https://www.tutorialspoint.com/sqlite/sqlite_python.htm
