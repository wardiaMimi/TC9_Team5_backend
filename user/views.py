from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from user.models import User,Annonce,Comment,Commande
from user import app, flask_bcrypt, db
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
import json
import pandas as pd
from pandas import json_normalize
import category_encoders as ce
import joblib as job
ma = Marshmallow(app)
# # DB Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','annonces_fav')
        include_relationships = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
class AnnonceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Annonce
        fields = ('id', 'name', 'year','mileage','engine','max_power','torque','seats','owner_id')

annonce_schema = AnnonceSchema()
annonces_schema = AnnonceSchema(many=True)


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'annonce_id')

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

jwt = JWTManager(app)




@app.route('/', methods=['GET'])
@jwt_required()
def index():
    return jsonify(message='Welcome to flask!')

# User routes
@app.route('/register', methods=['POST'])
def register():
    try :
      
      email = request.json['email']
      test = User.query.filter_by(email=email).first()
      if test:
          return jsonify(message='That email already exists'), 409
      else:
          
          username = request.json['username']
          password = request.json['password']
          pw_hash = flask_bcrypt.generate_password_hash(password, 10)
          user = User(username=username, email=email, password=pw_hash)
          db.session.add(user)
          db.session.commit()
          return jsonify(message='User created successfully'), 201
    except :
        return jsonify(message='Error Server'), 500

#all annonces 
@app.route('/all', methods=['GET'])
@jwt_required()
def all_annonces():
    try :

        annonce = Annonce.query.all()
        if annonce :
         return annonces_schema.dump(annonce)
        else :
            return jsonify(message='annonce does not exist'), 409
    except :
        return jsonify(message='Error Server'), 500


#annonces non vendus 
@app.route('/annonces', methods=['GET'])
@jwt_required()
def annonce_nonVendu():
    try :

        annonce = Annonce.query.filter_by(vendu = False).all()
        if annonce :
         return annonces_schema.dump(annonce)
        else :
            return jsonify(message='empty'), 409
    except :
        return jsonify(message='Error Server'), 500


#annonce favori 
@app.route('/favori/<int:id>', methods=['GET'])
@jwt_required()
def get_annonce_fav(id):    
    user = User.query.filter_by(id=id).first()
    if user :
     return user_schema.dump(user)
    else :
        return jsonify(message='annonce does not exist'), 409


# annonces  
@app.route('/annonce/<int:id>', methods=['GET'])
@jwt_required()
def get_annonce(id):
    annonce = Annonce.query.filter_by(owner_id = id)

    if annonce :
     return annonces_schema.dump(annonce)
    else :
        return jsonify(message='annonce does not exist'), 409



@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']


    test = User.query.filter_by(email=email).first()
   
    test_pw= flask_bcrypt.check_password_hash(test.password,password)
    if test and test_pw:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Successful', access_token=access_token)
    else:
        return jsonify('Bad email or Password'), 401




def add_annonce(data):

        model = job.load('/home/wardia/TC9/user/model.sav')
        dict = json.loads(data)
        df2 = json_normalize(dict)
        print(type(df2))
        encoder = ce.OrdinalEncoder(cols=['fuel', 'seller_type', 'transmission','mileage','owner'])
        Tester = encoder.fit_transform(df2)
        print(Tester)
        return model.predict(Tester)

def price_input(predicted_price,price):
    predicted_price_max =predicted_price +0.5
    predicted_price_min =predicted_price -0.5
    if price > predicted_price_min and price < predicted_price_max:
       return True
    else : return False


#predict price
@app.route('/predict', methods=['POST'])
@jwt_required()   
def predict_price(): 
    try:   
        data = { 
            'year' : request.json['year'],
           'km_driven' : request.json['km_driven'],
           'fuel' : request.json['fuel'],
           'seller_type' : request.json['seller_type'],
           'transmission' : request.json['transmission'],
           'owner' : request.json['owner'],
           'mileage' : request.json['mileage'],
           'engine' : request.json['engine'],
           'max_power' : request.json['max_power']}  

        json_string = json.dumps(data)
        predicted_price = int(add_annonce(json_string))
        print(predicted_price)
        return jsonify(message=predicted_price), 200
    
    except :
       return jsonify(message='Error Server'), 500




#add annonce 
@app.route('/add', methods=['POST'])
@jwt_required()   
def add(): 
    try:   
        name = request.json['name']
        seats =request.json['seats']
        selling_price = request.json['selling_price']
        torque =request.json['torque']
        year = request.json['year']
        km_driven = request.json['km_driven']
        transmission = request.json['transmission']
        seller_type = request.json['seller_type']
        owner = request.json['owner']
        mileage = request.json['mileage']
        engine = request.json['engine']
        max_power = request.json['max_power']
        fuel = request.json['fuel']
        owner_id = request.json['owner_id']
 

        predicted_price = request.json['predicted_price']

        if price_input(predicted_price,selling_price):
            user = Annonce(name=name,seats=seats,owner_id=owner_id,max_power=max_power,seller_type=seller_type,engine=engine,mileage=mileage, owner=owner,year=year,km_driven=km_driven,torque=torque,transmission=transmission,fuel=fuel, selling_price=selling_price)
            db.session.add(user)
            db.session.commit()
            return jsonify(message='annonce created successfully'), 201
        else :
          return jsonify(message='price Error'), 400

    except :
       return jsonify(message='Error Server'), 500


#like annonce
@app.route('/like', methods=['POST'])
@jwt_required()
def like():
    id = request.json['id']
    annonce_id = request.json['annonce_id']
    test = User.query.filter_by(id=id).first()
    annonce = Annonce.query.filter_by(id=annonce_id).first()
    print(annonce)
    
    if test:
        test.annonces_fav.append(annonce)
        db.session.commit()
        return jsonify(message='annonce liked successfully'), 201



#add comment
@app.route('/comment/<int:annonce_id>', methods=['POST'])
@jwt_required()
def comment(annonce_id):
    
    comment = request.json['content']
    annonce = Annonce.query.filter_by(id=annonce_id).first()
    if annonce:
        
        comment = Comment(content=comment, annonce_id=annonce_id) 
        db.session.add(comment)
        db.session.commit()
        return jsonify(message='annonce commented successfully'), 201

#delete comment
@app.route('/discomment/<int:comment_id>', methods=['POST'])
@jwt_required()
def discomment(comment_id):
    
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment:
        
        db.session.delete(comment)
        db.session.commit()
        return jsonify(message='annonce deleted successfully'), 201

#annonce comments 
@app.route('/comments/<int:annonce_id>', methods=['GET'])
@jwt_required()
def ann_comm(annonce_id):
    
    try :
        comms = Comment.query.filter_by(annonce_id=annonce_id)
        if comms :
         return comments_schema.dump(comms)
        else :
            return jsonify(message='comments does not exist'), 409
    except :
        return jsonify(message='Error Server'), 500



#dislike annonce
@app.route('/dislike', methods=['POST'])
@jwt_required()
def dislike():
    id = request.json['id']
    annonce_id = request.json['annonce_id']
    test = User.query.filter_by(id=id).first()
    annonce = Annonce.query.filter_by(id=annonce_id).first()
    print(annonce)
    
    if test:
        test.annonces_fav.remove(annonce)
        db.session.commit()
        return jsonify(message='annonce disliked  successfully'), 201
    



#modifier une annonce
@app.route('/modify', methods=['PUT'])
@jwt_required()
def modify():
        annonce_id =request.json['annonce_id']
        selling_price = request.json['selling_price']
        seats =request.json['seats']
        torque =request.json['torque']
        name = request.json['name']
        year = request.json['year']
        km_driven = request.json['km_driven']
        transmission = request.json['transmission']
        seller_type = request.json['seller_type']
        owner = request.json['owner']
        mileage = request.json['mileage']
        engine = request.json['engine']
        max_power = request.json['max_power']
        fuel = request.json['fuel']
        data = jsonify(
           year = request.json['year'],
           km_driven = request.json['km_driven'],
           transmission = request.json['transmission'],
           seller_type = request.json['seller_type'],
           owner = request.json['owner'],
           mileage = request.json['mileage'],
           engine = request.json['engine'],
           max_power = request.json['max_power'],
           fuel = request.json['fuel'],
        )
        dict = json.loads(data)
        df2 = json_normalize(dict['data']) 
        print(df2)
        # instance =dict(id =annonce_id, name=name,seats=seats,max_power=max_power,seller_type=seller_type,engine=engine,mileage=mileage, owner=owner,year=year,km_driven=km_driven,torque=torque,transmission=transmission,fuel=fuel, selling_price=selling_price)
        ann = Annonce.query.filter_by(id=annonce_id).first()
        if ann :
         ann.name = name
         ann.owner = owner
         ann.year = year
         ann.km_driven =km_driven
         ann.torque = torque
         ann.transmission = transmission
         ann.fuel = fuel
         ann.seller_type =seller_type
         ann.engine = engine
         ann.mileage =mileage
         ann.max_power = max_power
         ann.selling_price=selling_price
         ann.seats =seats
         db.session.commit()
         
         return jsonify(message='annonce updated successfully'), 201
        else : return jsonify(message='annonce does not exist '), 201
        


#delete annonce
@app.route('/delete/<int:annonce_id>', methods=['DELETE'])
@jwt_required()
def delete(annonce_id):
    # annonce_id =request.json['annonce_id']
    annonce = Annonce.query.filter_by(id=annonce_id).first()
    if annonce :
        db.session.delete(annonce)
        db.session.commit()
        return jsonify(message='annonce deleted successfully'), 201
    else :
        return jsonify(message='annonce does not exist'), 409

#buy annonce
@app.route('/buy/<int:buyer_id>/<int:annonce_id>', methods=['POST'])
@jwt_required()
def buy(annonce_id,buyer_id):
    
    annonce = Annonce.query.filter_by(id=annonce_id).first()
    #buyer
    buyer = User.query.filter_by(id=buyer_id).first()
    
    
    if annonce and buyer:
        commande = Commande(buyer=buyer.id,annonce_id=annonce.id)
        annonce.vendu = True
        annonce.owner_id = buyer.id
        db.session.add(commande)
        db.session.commit()
        return jsonify(message='annonce by successfully'), 201
    else :
        return jsonify(message='annonce does not exist'), 409






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
    file = open('', 'r')

    print('Database seeded')
