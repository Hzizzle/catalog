from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Cuisine, Recipe, User
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalog@localhost/recipecatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
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
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                                connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
            150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given \
                                            user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all the Cuisines
@app.route('/')
@app.route('/cuisines/')
def showCuisines():
    cuisines = session.query(Cuisine).order_by(asc(Cuisine.name))
    if 'username' not in login_session:
        return render_template('publiccuisines.html', cuisines=cuisines)
    else:
        return render_template('cuisines.html', cuisines=cuisines)


# Show the list of Recipes from a Cuisine
@app.route('/cuisines/<int:cuisine_id>/')
def showRecipeList(cuisine_id):
    cuisine = session.query(Cuisine).filter_by(id=cuisine_id).one()
    recipes = session.query(Recipe).filter_by(
        cuisine_id=cuisine_id).all()
    if 'username' not in login_session:
        return render_template('publicrecipelist.html', recipes=recipes,
                               cuisine=cuisine)
    else:
        return render_template('recipelist.html', recipes=recipes,
                               cuisine=cuisine)


# Show a Recipe description
@app.route('/cuisines/<int:cuisine_id>/<int:recipe_id>')
def showRecipe(cuisine_id, recipe_id):
    cuisine = session.query(Cuisine).filter_by(id=cuisine_id).one()
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return render_template('recipe.html', recipe=recipe, cuisine=cuisine)


# Create a new Recipe for a given Cuisine
@app.route('/cuisines/<int:cuisine_id>/new/', methods=['GET', 'POST'])
def newRecipe(cuisine_id):
    if 'username' not in login_session:
        return redirect('/login')
    cuisine = session.query(Cuisine).filter_by(id=cuisine_id).one()
    if request.method == 'POST':
        newRecipe = Recipe(name=request.form['name'],
                           description=request.form['description'],
                           cuisine_id=cuisine_id,
                           user_id=login_session['user_id'])
        session.add(newRecipe)
        session.commit()
        flash('New Recipe %s Successfully Created' % (newRecipe.name))
        return redirect(url_for('showRecipeList', cuisine_id=cuisine_id))
    else:
        return render_template('newrecipe.html', cuisine_id=cuisine_id)


# Edit a Recipe description
@app.route('/cuisines/<int:cuisine_id>/<int:recipe_id>/edit',
           methods=['GET', 'POST'])
def editRecipe(cuisine_id, recipe_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedrecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    cuisine = session.query(Cuisine).filter_by(id=cuisine_id).one()
    if login_session['user_id'] != editedrecipe.user_id:
        return "<script>function myFunction() {alert('You are not authorized\
                to edit this recipe. Please create your a seperate recipe that\
                you can edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedrecipe.name = request.form['name']
        if request.form['description']:
            editedrecipe.description = request.form['description']
        session.add(editedrecipe)
        session.commit()
        flash('Recipe Successfully Edited')
        return redirect(url_for('showRecipeList', cuisine_id=cuisine_id))
    else:
        return render_template('editrecipe.html', cuisine_id=cuisine_id,
                               recipe_id=recipe_id, recipe=editedrecipe)


# Delete a Recipe
@app.route('/cuisines/<int:cuisine_id>/<int:recipe_id>/delete',
           methods=['GET', 'POST'])
def deleteRecipe(cuisine_id, recipe_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleterecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    cuisine = session.query(Cuisine).filter_by(id=cuisine_id).one()
    if login_session['user_id'] != deleterecipe.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
                to delete this recipe. Please create your own recipe in order \
                to delete it.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(deleterecipe)
        session.commit()
        flash('Recipe Successfully Deleted')
        return redirect(url_for('showRecipeList', cuisine_id=cuisine_id))
    else:
        return render_template('deleterecipe.html', cuisine_id=cuisine_id,
                               deleterecipe=deleterecipe)


# Disconnect
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCuisines'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCuisines'))


# JSON API code for querying all recipes entered so far
@app.route('/cuisines/JSON')
def recipesJSON():
    recipes = session.query(Recipe).all()
    return jsonify(recipe=[r.serialize for r in recipes])


# JSON API code for querying a recipe if you know the cuisine and recipe ids
@app.route('/cuisines/<int:cuisine_id>/<int:recipe_id>/JSON')
def recipeJSON(recipe_id, cuisine_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return jsonify(recipe=recipe.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
