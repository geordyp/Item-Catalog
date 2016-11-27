from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from functools import wraps

import string
import random
import json
import httplib2
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog Project'


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    """ Display login page for the user to sign in """
    # Create anti-forgery state token to prevent request forgery
    # Store it in the session for later validation
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return 'The current session state is %s' % login_session['state']
    user = ''
    if 'username' in login_session:
        user = login_session['username']

    return render_template('login.html',
                           STATE=state,
                           user=user)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Handles the code sent back from the callback method """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps('Tokens user ID doesnt match given user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps('Tokens client ID does not match apps.'), 401)
        print 'Tokens client ID does not match apps.'
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ Log a user out of the application """
    # Revoke a current user's token and reset their login_session
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return redirect('/recommendations')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    """ Create a new user and store them in the database """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Get a user from the database with the given id """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ Get a user's id with the given email """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def isUserLoggedIn():
    """ If a user is logged in, return the current user """
    if 'username' in login_session:
        userID = getUserID(login_session['email'])
        return getUserInfo(userID)
    return None


@app.route('/recommendations/categories/JSON')
def recommendationsJSON():
    """ Returns a JSON of all the categories """
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/recommendations/<string:category_name>/JSON')
def categoryJSON(category_name):
    """ Returns a JSON of all the items of a specified category """
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/recommendations/JSON')
def recommendationsJSON():
    """ Returns a JSON of all the items """
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


def login_required(f):
    """ Function decorator for functions that require logins """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if user is logged in
        user = isUserLoggedIn()
        if not user:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/recommendations')
def showRecommendations():
    """ Show the home page, all recommendations (items) """
    # retrieve data
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id)).limit(10)

    # check if user is logged in
    user = isUserLoggedIn()

    return render_template('items.html',
                           itemHeading='Latest Recommendations',
                           categories=categories,
                           items=items,
                           home=True,
                           user=user)


@app.route('/recommendations/<string:category_name>')
@app.route('/recommendations/<string:category_name>/items')
def showCategory(category_name):
    """ Show recommendations (items) from the specified category """
    # retrieve data
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).order_by(desc(Item.id))

    # check if user is logged in
    user = isUserLoggedIn()

    return render_template('items.html',
                           itemHeading='Recommendations in ' + category_name,
                           categories=categories,
                           items=items,
                           home=False,
                           user=user)


@app.route('/recommendations/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    """ Show a specific recommendation (item) and it's info """
    # retrieve data
    item = session.query(Item).filter_by(title=item_name).one()

    # check if user is logged in
    user = isUserLoggedIn()

    canEdit = False
    if user and user == item.user:
        canEdit = True

    return render_template('item.html',
                           item=item,
                           user=user,
                           canEdit=canEdit)


@app.route('/recommendations/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """ Show a form to create a new recommendation (item) """
    # retrieve data
    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'POST':
        if request.form['title'] and request.form['description']:
            newItem = Item(title=request.form['title'],
                           description=request.form['description'],
                           category_id=request.form['category'],
                           user=user)
            session.add(newItem)
            session.commit()
            return redirect(url_for('showRecommendations'))
        else:
            error = 'Please include a title and description.'
            return render_template('new_item.html',
                                   categories=categories,
                                   title=request.form['title'],
                                   description=request.form['description'],
                                   error=error,
                                   user=user)
    else:
        return render_template('new_item.html',
                               categories=categories,
                               title='',
                               description='',
                               error='',
                               user=user)


@app.route('/recommendations/<string:item_name>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    """ Show a form to edit a specific recommendation (item) """
    # retrieve data
    categories = session.query(Category).order_by(asc(Category.name))
    editedItem = session.query(Item).filter_by(title=item_name).one()

    # make the user created the item they're about to edit
    if user != editedItem.user:
        return redirect(url_for('showItem',
                                category_name=editedItem.category.name,
                                item_name=editedItem.title))

    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']

        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItem',
                                category_name=editedItem.category.name,
                                item_name=editedItem.title))
    else:
        return render_template('edit_item.html',
                               categories=categories,
                               item=editedItem,
                               user=user)


@app.route('/recommendations/<string:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    """ Show a form to delete a specific recommendation (item) """
    # retrieve data
    deletedItem = session.query(Item).filter_by(title=item_name).one()

    # make the user created the item they're about to delete
    if user != deletedItem.user:
        return redirect(url_for('showItem',
                                category_name=deletedItem.category.name,
                                item_name=deletedItem.title))

    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        return render_template('delete_confirmation.html',
                               item=deletedItem,
                               user=user)
    else:
        return render_template('delete_item.html',
                               item=deletedItem,
                               user=user)


if __name__ == '__main__':
    app.secret_key = 'super_duper_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
