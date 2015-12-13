from flask import Flask

app = Flask(__name__)

# I've created the routes to support the screenshots from the "Getting Started"
# guide, but I've also added more RESTful looking APIs which would be more
# intuitive to a developer from an API perspective.

@app.route('/')
@app.route('/catalog')
def index():
	return "Index"
	
@app.route('/catalog/categories/<category>')
@app.route('/catalog/<category>')
def category(category):
	return "Category Page"

@app.route('/catalog/items/<item>')
@app.route('/catalog/<category>/<item>')
def item(category, item):
	return "Item Page"
	
@app.route('/catalog/items/<item>/edit')
@app.route('/catalog/<category>/<item>/edit')	
def item_edit(item):
	return "Item Edit Page"
	
@app.route('/catalog/items/<item>/delete')
@app.route('/catalog/<category>/<item>/delete')
def item_delete(item):
	return "Item Deletion Page"
	
# JSON API
# TODO: Consolidate this based on extension
@app.route('/catalog.json')
def index_json():
	return "{ 'page':'index' }"
	
	
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)