import sys, random, string

from flask import Flask, render_template, g, request, flash, redirect, abort, url_for, jsonify
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from database_setup import Item, Category, User

## Application Setup ##
app = Flask(__name__)

cfgFile = 'config'
if(len(sys.argv) > 1):
    cfgFile = str(sys.argv[1])
app.config.from_object(cfgFile)
app.config.from_object("secrets")
app.logger.debug("Loaded config file: '%s'" % cfgFile)

secrets = json.loads(
    open('client_secrets.json', 'r').read())
app.config['CLIENT_ID'] = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine(app.config["DB_STRING"], echo=app.config["DB_ECHO"])
Session = sessionmaker()
Session.configure(bind=engine)

## Administrative Methods ##

@app.before_request
def before_request():
    g.s = Session() 

@app.teardown_request
def teardown_request(exception):
    g.s.close()

@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template(
        "login.html", 
        client_id=app.config["CLIENT_ID"], 
        login_session=login_session)

@app.route('/gconnect/', methods=['POST'])
def gconnect():
    # Deal with state mismatch shennanigans
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] 
        return response
        
    # Exchange google's code for the access token
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Get the access token
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    
    # Make sure this is the user we're looking for
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID oesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Check to see if they're already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Store their login credentials
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    
    login_session['user'] = get_or_create_user( data ).serialize
    
    output = ''
    output += '<h1>Welcome, %s!</h1>' % login_session['user']['name']
    output += '<img src="%s" style = "width: 150px; height: 150px; border-radius: 75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;">' % login_session['user']['picture']
    flash("You are now logged in as %s" % login_session['user']['name'])
    return output
    
def get_or_create_user( data ):
    # Check to see if that user exists
    user = g.s.query(User).filter(User.google_id == data["id"]).first()
    if user is None:
        user = User(
            name=data['name'],
            google_id=data['id'],
            picture=data['picture']
            )
        g.s.add(user)
        g.s.commit()
    return user


@app.route("/logout/")
def logout():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] != '200':
        app.logger.error('Failed to revoke token for given user: %s.' % login_session['user'].name)
        
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['user']
    flash("You are now logged out.")
    return redirect(url_for('index'))

@app.route('/')
@app.route('/catalog/')
def index():
    categories = g.s.query(Category).all()
    items = g.s.query(Item).order_by(desc(Item.id)).limit(5)
    return render_template(
        "index.html", 
        categories=categories, 
        items=items, 
        login_session=login_session)

## Item Routing ##

@app.route('/catalog/items/', methods=["GET"])
def list_items():
    # Load the page
    items = g.s.query(Item).all()
    return render_template(
        'list_items.html', 
        items=items, 
        login_session=login_session)
@app.route('/catalog/items.json/', methods=["GET"])
def list_items_json():
    items = g.s.query(Item).all()        
    return jsonify(Items=[i.serialize for i in items])

        
@app.route('/catalog/items/add/', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        if not login_session.get('user'):
            abort(401)
        categories = g.s.query(Category).all()
        return render_template(
            'add_item.html', 
            categories=categories, 
            login_session=login_session)
    else:
        g.s.add(
            Item(
                name=       request.form['name'], 
                description=request.form['description'], 
                category_id=request.form['category_id'],
                user_id=    request.form['user_id']))
        g.s.commit()
        flash("'%s' has been created succesfully!" % request.form['name'])
        return redirect(url_for('list_items'))
    
@app.route('/catalog/items/<int:item_id>/', methods=['GET'])
def view_item(item_id):
    item = g.s.query(Item).filter(Item.id == item_id).first()
    return render_template(
        'view_item.html', 
        item=item, 
        login_session=login_session)
@app.route('/catalog/items/<int:item_id>.json/', methods=['GET'])
def view_item_json(item_id):
    item = g.s.query(Item).filter(Item.id == item_id).first()
    return jsonify(item.serialize)

@app.route('/catalog/items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    if not login_session.get('user'):
        abort(401)
    if request.method == 'GET':
        item = g.s.query(Item).filter(Item.id == item_id).first()
        if login_session.get('user')['id'] is not item.owner_id:
            abort(401)
        categories = g.s.query(Category).all()
        return render_template(
            'edit_item.html', 
            item=item, 
            categories=categories, 
            login_session=login_session)
    else:
        g.s.query(Item).filter(Item.id==request.form['id']).update(
            {"name":        request.form['name'], 
            "description":  request.form['description'], 
            "category_id":  request.form['category_id']})
        g.s.commit()
        flash("'%s' has been updated succesfully!" % request.form['name'])
        return redirect(url_for('view_item', item_id=item_id))
	
@app.route('/catalog/items/<int:item_id>/delete', methods=['GET','POST'])
def delete_item(item_id):
    if not login_session.get('user'):
        abort(401)
    if request.method=='POST':
        g.s.query(Item).filter(Item.id==item_id).delete()
        g.s.commit()
        flash("The item has been deleted successfully!")
        return redirect(url_for('list_items'))
    else:
        item = g.s.query(Item).filter(Item.id == item_id).first()
        return render_template(
            'delete_item.html', 
            item=item, 
            login_session=login_session)

## Category Routing ##

@app.route('/catalog/categories/')
def list_categories():
    categories = g.s.query(Category).all()
    return render_template(
        'list_categories.html', 
        categories=categories, 
        login_session=login_session)
@app.route('/catalog/categories.json/')
def list_categories_json():
    categories = g.s.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

@app.route('/catalog/categories/add/', methods=['GET','POST'])
def add_category():
    if not login_session.get('user'):
        abort(401)
    if request.method=='GET':
        return render_template(
            'add_category.html',
            login_session=login_session)
    else:
        g.s.add(Category(
            name=request.form['name'], 
            user_id=request.form['user_id']))
        g.s.commit()
        flash("'%s' has been created successfully!" % request.form['name'])
        return redirect(url_for('list_categories'))

@app.route('/catalog/categories/<int:category_id>/')
def view_category(category_id):
    category = g.s.query(Category).filter(Category.id==category_id).first()
    return render_template('view_category.html', 
        category=category,
        login_session=login_session)
@app.route('/catalog/categories/<int:category_id>.json/')
def view_category_json(category_id):
    category = g.s.query(Category).filter(Category.id==category_id).first()
    return jsonify(category.serialize)
    
@app.route('/catalog/categories/<int:category_id>/edit', methods=['GET','POST'])
def edit_category(category_id):
    if not login_session.get('user'):
        abort(401)
    if request.method == 'GET':
        category = g.s.query(Category).filter(Category.id==category_id).first()
        if login_session.get('user')['id'] != category.user_id:
            abort(401)
        return render_template(
            'edit_category.html', 
            category=category, 
            login_session=login_session)
    else:
        g.s.query(Category).filter(Category.id==category_id).update({
            "name":request.form['name']})
        g.s.commit()
        flash("'%s' has been updated successfully!" % request.form['name'])
        return redirect(url_for('view_category', category_id=category_id))
    
@app.route('/catalog/categories/<int:category_id>/delete', methods=['GET','POST'])
def delete_category(category_id):
    if not login_session.get('user'):
        abort(401)
    if request.method == 'GET':
        category = g.s.query(Category).filter(Category.id==category_id).first()
        return render_template(
            'delete_category.html', 
            category=category, 
            login_session=login_session)
    else:
        g.s.query(Category).filter(Category.id==category_id).delete()
        g.s.commit()
        flash("The category has been deleted successfully!")
        return redirect(url_for('list_categories'))
        
## Error Pages ##

@app.errorhandler(401)
def access_denied(error):
    app.logger.warning('Access Denied: %s' % error)
    return render_template('access_denied.html', login_session=login_session), 401
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
    
@app.errorhandler(500)
def internal_error(error):
    return render_template('internal_error.html'), 500

## App Server Code ##
if __name__ == '__main__':
	app.debug = app.config['DEBUG']
	app.run(host = '0.0.0.0', port = 8080)
