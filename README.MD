# Insallation Instructions
1.  Add a file called "secrets.py" in the catalog folder with a SECRET_KEY
    variable with a unique GUID like below:
    SECRET_KEY="YOUR-GUID-HERE"
2.  Add a file called "client_secrets.json" in the catalog with your own client 
    secrets file from google. See client_secrets.json.example.
3.  Run "vagrant up"
4.  Run "vagrant ssh"
5.  Change directory to /vagrant/catalog
6.  Run "python database_setup.py"
7.  Run "python catalog.py"

Open a browser to localhost:8080

# Credits

SQLAlchemy 	    Tutorials/Docs 	- sqlalchemy.org
Flask 		    Tutorials/Docs 	- pocoo.org
HTML 		    Reference 	    - w3.org
Script Order    Tutorials       - html5rocks.com/en/tutorials/speed/script-loading/
Udacity         Tutorials       - udacity.com
Cascading Deletes               - http://stackoverflow.com/questions/5033547/sqlachemy-cascade-delete
