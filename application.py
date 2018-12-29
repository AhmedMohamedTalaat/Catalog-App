#!/usr/bin/python3.6
import json
import random
import requests
import string
import httplib2
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Categories, Items
from flask import session as login_session

app = Flask(__name__)
# Read secret json file for access account
CLIENT_ID = json.loads(open('catalog_secret.json', 'r').read())[
    'web']['client_id']
print("Client id :{}".format(CLIENT_ID))
# implement database connection
engine = create_engine("sqlite:///catalogApp.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# ======================JSON==============================
@app.route('/categories/json')
def all_categories_json():
    cates = session.query(Categories).all()
    categories_json = [cate.serialize for cate in cates]
    for category in categories_json:
        items = session.query(Items).filter_by(cate_id=category['id']).all()
        items_json = [item.serialize for item in items]
        if items_json:
            category['items'] = items_json
    return jsonify(categories_json)


# ========================================================
@app.route('/')
@app.route('/catalog')
def all_catalog():
    categories = session.query(Categories).all()
    items = session.query(Items).all()
    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog/<string:category_name>/items')
def items_per_category(category_name):
    categories = session.query(Categories).all()
    category = session.query(Categories).filter_by(name=category_name).one()
    print(category.name)
    if category:
        items = session.query(Items).filter_by(cate_id=category.id).all()
        print([item.name for item in items])
        return render_template('items_per_catalog.html',
                               categories=categories,
                               selected_category=category,
                               items=items)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def item_description(category_name, item_name):
    category = session.query(Categories).filter_by(name=category_name).first()
    print(category_name)
    if category:
        item = session.query(Items).filter_by(
            cate_id=category.id, name=item_name).first()
        if item:
            return render_template('item_description.html', category=category, item=item)
        else:
            return "No description for this item"
    else:
        return "we can't find your category"


# worked and need to add login session
@app.route('/catalog/new_item', methods=['GET', 'POST'])
def add_new_item():
    categories = session.query(Categories).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        new_item = Items(cate_id=request.form['category_id'],
                         name=request.form['title'],
                         description=request.form['description'])
        session.add(new_item)
        session.commit()
        return redirect(url_for("all_catalog"))
    else:
        return render_template("add_item.html", categories=categories)


# worked and need to add login session and form
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def update_item(category_name, item_name):
    allCategory = session.query(Categories).all()
    category = session.query(Categories).filter_by(name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Items).filter_by(
        cate_id=category.id, name=item_name).one()
    print(item.name, item.description)
    if request.method == "POST":
        if category.user_id !=login_session['user_id']:
                return "<script>function myFunction() {alert('You\
                        are not authorized to update this item.\
                        Please create your own item in order\
                        to delete.');}</script><body onload='myFunction()'>"
        else:
            if request.form['title']:
                item.name = request.form['title']
            if request.form['description']:
                item.description = request.form['description']
            if request.form['category_id']:
                item.cate_id = request.form['category_id']
            session.add(item)
            session.commit()
            return redirect(url_for("all_catalog"))
    else:
        return render_template("edit_item.html", item=item, categories=allCategory)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(cate_id=category.id, name=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        if category.user_id !=login_session['user_id']:
            return "<script>function myFunction() {alert('You\
                    are not authorized to delete this item.\
                    Please create your own item in order\
                    to delete.');}</script><body onload='myFunction()'>"
        else:
            session.delete(item)
            session.commit()
            return redirect(url_for("all_catalog"))
    else:
        return render_template("delete_item.html", item=item)
   


# =========================================================
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    print("login session : {}".format(login_session['state']))
    return render_template("login.html", STATE=state)


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def create_user(loginsession):
    newUser = User(name=loginsession['username'],
                   email=loginsession['email'],
                   )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=loginsession['email']).one()
    return user.id


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print("Resquest args:", request.args.get('state'))
    print("login session :", login_session['state'])
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('catalog_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print("access token:", access_token)
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    print("url :", url)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print("gplus :", gplus_id)
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('all_catalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=5000)
