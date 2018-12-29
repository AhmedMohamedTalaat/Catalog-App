# Catalog App 
this app for view category and their items and make CRUD function if you have the access by login or you can view if you don't have access

# Requirments

  - Flask
  - postgreSQL
  - SQLite
  - oauth2client
  - Bootstrap



### Installation
create virtual env to install requiement into it
```sh
$ pip3 install virtualenv
$ virtualenv -p python3 myenv
$ source myenv/bin/activate
$ pip install -r requirements.txt 
```
### Functions

|                |Description                          |Params                         |
|----------------|-------------------------------|---------------------------|
|all_categories_json|`return all data at json format`            |No params            |
|items_per_category          |`return items per category`            |category name   |         |
|item_description          |`return description for each item`|category name,item name
|add_new_item               | `redirect to a form to insert new item`|No Params
|update_item|`update selected item`|category name,item name|
|delete_item | `delete selected item`|category name,item name|
|show_login|`redirect to google sign in `|No params|
|get_user_id|`take user email and return id from DB`|email|
|get_user_info|`take user id and return all info about it`|user_id|
|create_user|`take session to create new user`|login_session|
|gconnect|`make connection  with google to get access`|No params
|gdisconnect|`disconnect from google by delete session info`|No params

# Running the app 
  - `python models.py` to install database
  - `python insertDummy.py` to fill the database
  - `python application.py` to run app

Verify server address in your preferred browser.

```sh
127.0.0.1:5000
```

  

