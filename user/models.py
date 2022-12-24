from user import db
from flask_marshmallow import Marshmallow
from user import app
import sqlalchemy.types as types
ma = Marshmallow(app)

class MyType(types.TypeDecorator):
    impl = types.String
    cache_ok = True
    def __init__(self, choices):
        self.choices = tuple(choices)
        self.internal_only = True

# Database models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), )
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    # annonce = db.relationship('annonces',backref="owned_user")
    
# DB Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')


# Marsh mellow db adds
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Annonce(db.Model):
    __tablename__ = 'annonces'
 
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String() ,nullable=False)
    year = db.Column(db.String(4),nullable=False)
    selling_price = db.Column(db.String, nullable=False)
    km_driven = db.Column(db.String)
    transmission = MyType(["Manual","Automatic"])
    fuel = MyType(["Diesel","Petrol","LPG", "CNG"])
    seller_type = MyType(['Individual','Dealer', 'TrustMark Dealer'])
    owner = db.Column(db.Integer ,nullable=False)
    mileage = db.Column(db.String,nullable=False)
    engine= db.Column(db.String(),nullable=False)
    max_power = db.Column(db.String,nullable=False)
    troque = db.Column(db.String(),nullable=False)
    seats = db.Column(db.Integer,nullable=False)
    owner_id = db.Column(db.Integer(),db.ForeignKey('users.id'))


