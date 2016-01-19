from flask import Flask, render_template, g, request, flash, redirect, url_for
from sqlalchemy import create_engine
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
	return render_template("index.html")

@app.route('/catalog/items/', methods=["GET", "POST"])
def item_list():
    if request.method == 'POST':
        # Read the post
        name = request.form['name']
        description = request.form['description']
        category_id = request.form['category_id']
        # Handle update requests
        if 'id' in request.form:
            id = request.form['id']
            g.s.query(Item).filter(Item.id==id).update(
                {"name":name, 
                "description":description, 
                "category_id":category_id})
            g.s.commit()
            flash("'%s' has been updated succesfully!" % name)
        # Handle creation requests
        else:
            g.s.add(
                Item(
                    name=name, 
                    description=description, 
                    category_id=category_id))
            g.s.commit()
            flash("'%s' has been created succesfully!" % name)
    # Load the page
    items = g.s.query(Item).all()
    return render_template('list_items.html', items=items)
    
@app.route('/catalog/items/add/')
def item_add():
    categories = g.s.query(Category).all()
    return render_template('add_item.html', categories=categories)
    
@app.route('/catalog/items/<int:item_id>', methods=['GET'])
def item_view(item_id):
    item = g.s.query(Item).filter(Item.id == item_id).first()
    return render_template('view_item.html', item=item)
	
@app.route('/catalog/items/<item_id>/edit')
def item_edit(item_id):
    item = g.s.query(Item).filter(Item.id == item_id).first()
    categories = g.s.query(Category).all()
    return render_template('edit_item.html', item=item, categories=categories)
	
@app.route('/catalog/items/<item_id>/delete', methods=['GET','POST'])
def item_delete(item_id):
    if request.method=='POST':
        g.s.query(Item).filter(Item.id==item_id).delete()
        g.s.commit()
        flash("The item has been deleted successfully!")
        return redirect(url_for('item_list'))
    else:
        item = g.s.query(Item).filter(Item.id == item_id).first()
        return render_template('delete_item.html', item=item)
	
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
