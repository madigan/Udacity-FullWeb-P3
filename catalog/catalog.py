from flask import Flask, render_template, g, request, flash, redirect, url_for
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import sys
from database_setup import Item, Category

app = Flask(__name__)

cfgFile = 'config'
if(len(sys.argv) > 1):
    cfgFile = str(sys.argv[1])
app.config.from_object(cfgFile)
app.logger.debug("Loaded config file: '%s'" % cfgFile)

engine = create_engine(app.config["DB_STRING"], echo=app.config["DB_ECHO"])
Session = sessionmaker()
Session.configure(bind=engine)

@app.before_request
def before_request():
    g.s = Session() 

@app.teardown_request
def teardown_request(exception):
    g.s.close()

@app.route('/')
@app.route('/catalog/')
def index():
    categories = g.s.query(Category).all()
    items = g.s.query(Item).order_by(desc(Item.id)).limit(5)
    return render_template("index.html", categories=categories, items=items)

## Item Routing ##

@app.route('/catalog/items/', methods=["GET"])
def list_items():
    # Load the page
    items = g.s.query(Item).all()
    return render_template('list_items.html', items=items)
    
@app.route('/catalog/items/add/', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        categories = g.s.query(Category).all()
        return render_template('add_item.html', categories=categories)
    else:
        g.s.add(
            Item(
                name=       request.form['name'], 
                description=request.form['description'], 
                category_id=request.form['category_id']))
        g.s.commit()
        flash("'%s' has been created succesfully!" % request.form['name'])
        return redirect(url_for('list_items'))
    
@app.route('/catalog/items/<int:item_id>', methods=['GET'])
def view_item(item_id):
    item = g.s.query(Item).filter(Item.id == item_id).first()
    return render_template('view_item.html', item=item)
	
@app.route('/catalog/items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'GET':
        item = g.s.query(Item).filter(Item.id == item_id).first()
        categories = g.s.query(Category).all()
        return render_template('edit_item.html', item=item, categories=categories)
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
    if request.method=='POST':
        g.s.query(Item).filter(Item.id==item_id).delete()
        g.s.commit()
        flash("The item has been deleted successfully!")
        return redirect(url_for('list_items'))
    else:
        item = g.s.query(Item).filter(Item.id == item_id).first()
        return render_template('delete_item.html', item=item)

## Category Routing ##

@app.route('/catalog/categories/')
def list_categories():
    categories = g.s.query(Category).all()
    return render_template('list_categories.html', categories=categories)

@app.route('/catalog/categories/add/', methods=['GET','POST'])
def add_category():
    if request.method=='GET':
        return render_template('add_category.html')
    else:
        g.s.add(Category(name=request.form['name']))
        g.s.commit()
        flash("'%s' has been created successfully!" % request.form['name'])
        return redirect(url_for('list_categories'))

@app.route('/catalog/categories/<int:category_id>/')
def view_category(category_id):
    category = g.s.query(Category).filter(Category.id==category_id).first()
    return render_template('view_category.html', category=category)
    
@app.route('/catalog/categories/<int:category_id>/edit', methods=['GET','POST'])
def edit_category(category_id):
    if request.method == 'GET':
        category = g.s.query(Category).filter(Category.id==category_id).first()
        return render_template('edit_category.html', category=category)
    else:
        g.s.query(Category).filter(Category.id==category_id).update({
            "name":request.form['name']})
        g.s.commit()
        flash("'%s' has been updated successfully!" % request.form['name'])
        return redirect(url_for('view_category', category_id=category_id))
    
@app.route('/catalog/categories/<int:category_id>/delete', methods=['GET','POST'])
def delete_category(category_id):
    if request.method == 'GET':
        category = g.s.query(Category).filter(Category.id==category_id).first()
        return render_template('delete_category.html', category=category)
    else:
        g.s.query(Category).filter(Category.id==category_id).delete()
        g.s.commit()
        flash("The category has been deleted successfully!")
        return redirect(url_for('list_categories'))

## App Server Code ##
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
