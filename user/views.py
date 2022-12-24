from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from user.models import User,Annonce
from user import app
from user import db

jwt = JWTManager(app)

@app.route('/', methods=['GET'])
@jwt_required()
def index():
    return jsonify(message='Welcome to flask!')

# User routes
@app.route('/register', methods=['POST'])
def register():
    email = request.json['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists'), 409
    else:
        
        username = request.json['username']
        password = request.json['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created successfully'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Successful', access_token=access_token)
    else:
        return jsonify('Bad email or Password'), 401



# annonce routes

@app.route('/add', methods=['POST'])
@jwt_required()
def add():    
        name = request.json['name']
        year = request.json['year']
        selling_price = request.json['selling_price']
        km_driven = request.json['km_driven']
        transmission = request.json['transmission']
        seller_type = request.json['seller_type']
        owner = request.json['owner']
        mileage = request.json['mileage']
        engine = request.json['engine']
        max_power = request.json['max_power']
        troque =request.json['troque']
        fuel = request.json['fuel']
        seats =request.json['seats']
        owner_id = request.json['owner_id']
        test = User.query.filter_by(id=owner_id).first()
        if test :
          user = Annonce(name=name,seats=seats,owner_id=owner_id,max_power=max_power,seller_type=seller_type,engine=engine,mileage=mileage, owner=owner,year=year,km_driven=km_driven,troque=troque,transmission=transmission,fuel=fuel, selling_price=selling_price)
          db.session.add(user)
          db.session.commit()
          return jsonify(message='annonce created successfully'), 201
        else :
          return jsonify(message='user Does not exist'), 409
       


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():
    test_user = User(first_name='Stephen',
                     last_name='Hawking',
                     email='admin@admin.com',
                     password='admin')
    db.session.add(test_user)
    db.session.commit()
    print('Database seeded')
