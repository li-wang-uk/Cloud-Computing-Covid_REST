from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import requests_cache
import urllib.parse


params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=test-covid-server.database.windows.net;DATABASE=test1_db;UID=azureuser;PWD=covid&20882") # store parameters to access to an external DB server


requests_cache.install_cache('covid_api_cache', backend='sqlite', expire_after=36000) # create a cache to store the data from external API. The expiration time is 36000 seconds.
app = Flask(__name__)
app.config["SECRET_KEY"] = "d4a7fbed321f7258a8b607748b458180" # set a secret key to hash user passwords
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params # access to the external DB server
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app) # create a db
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from covid import routes