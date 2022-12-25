from user import db
from user import app
import sqlalchemy.types as types
from werkzeug.security import generate_password_hash, check_password_hash

# Database models

annonce_user = db.Table('annonce_user',
                    db.Column('annonce_id', db.Integer, db.ForeignKey('annonces.id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                    )

commetns_user = db.Table('comments_user',
                    db.Column('annonce_id', db.Integer, db.ForeignKey('annonces.id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'))

                    )






class MyType(types.TypeDecorator):
    impl = types.String
    cache_ok = True
    def __init__(self, choices):
        self.choices = tuple(choices)
        self.internal_only = True

class User(db.Model):
    __tablename__ = 'users'
    serialize_only=()
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), )
    email = db.Column(db.String,nullable=False,unique=True)
    password = db.Column(db.String)
    annonces_fav = db.relationship('Annonce',secondary='annonce_user', backref = 'users')
    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    annonce_id = db.Column(db.Integer, db.ForeignKey('annonces.id'))

class Commande(db.Model):
    __tablename__ = 'commandes'
    id = db.Column(db.Integer, primary_key=True)
    buyer = db.Column(db.Integer, db.ForeignKey('users.id'))
    annonce_id = db.Column(db.Integer, db.ForeignKey('annonces.id'))

class Annonce(db.Model):
    __tablename__ = 'annonces'
 
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String() ,nullable=False)
    year = db.Column(db.Integer(),nullable=False)
    selling_price = db.Column(db.String, nullable=False)
    km_driven = db.Column(db.Integer())
    transmission =  db.Column(db.String() ,nullable=False)
    fuel =  db.Column(db.String() ,nullable=False)
    seller_type =  db.Column(db.String() ,nullable=False)
    owner =  db.Column(db.String() ,nullable=False)
    # transmission =  MyType(["Manual","Automatic"])
    # fuel = MyType(["Diesel","Petrol","LPG", "CNG"])
    # seller_type = MyType(['Individual','Dealer', 'TrustMark Dealer'])
    # owner =  MyType(['First Owner','Second Owner', 'Third Owner','Fourth & Above Owner'])
    mileage = db.Column(db.Float(),nullable=False)
    engine= db.Column(db.Integer(),nullable=False)
    max_power = db.Column(db.Float(),nullable=False)
    torque = db.Column(db.String(),nullable=False)
    seats = db.Column(db.Integer,nullable=False)
    vendu= db.Column(db.Boolean(),default=False)
    owner_id = db.Column(db.Integer(),db.ForeignKey('users.id')) 
    

