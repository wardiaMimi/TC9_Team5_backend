from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_cors import CORS
from flask_bcrypt import Bcrypt
app = Flask(__name__)
CORS(app)
flask_bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True 
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change on production



db = SQLAlchemy(app)



from user import views














