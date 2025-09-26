"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, FavoritePlanet, FavoriteCharacter
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/hello', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /hello response "
    }
    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets =Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user = User.query.first()
    if current_user is None:
        return jsonify({"msg": "No users found"}), 404
    
    favorite_planets = [fav.planet.serialize() for fav in current_user.favorite_planets]
    favorite_characters = [fav.character.serialize() for fav in current_user.favorite_characters]

    return jsonify({
        "favorite_planets": favorite_planets,
        "favorite_characters": favorite_characters
    }), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user = User.query.first()
    if current_user is None:
        return jsonify({"msg": "No users found"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    
    existing_favorite = FavoritePlanet.query.filter_by(
        user_id=current_user.id,
        planet_id=planet_id
    ).first()

    if existing_favorite:
        return jsonify({"msg": "Planet already in favorites"}), 400
    
    new_favorite = FavoritePlanet(user_id=current_user.id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user = User.query.first()
    if current_user is None:
        return jsonify({"msg": "No users found"}), 404
    
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    
    existing_favorite = FavoriteCharacter.query.filter_by(
        user_id=current_user.id,
        character_id=people_id
    ).first()

    if existing_favorite:
        return jsonify({"msg": "Character already in favorites"}), 400
    
    new_favorite = FavoriteCharacter(user_id=current_user.id, character_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Character added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user = User.query.first()
    if current_user is None:
        return jsonify({"msg": "No users found"}), 404
    
    favorite = FavoritePlanet.query.filter_by(
        user_id=current_user.id,
        planet_id=planet_id
    ).first()

    if favorite is None:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Planet removed from favorites"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user = User.query.first()
    if current_user is None:
        return jsonify({"msg": "No users found"}), 404
    
    favorite = FavoriteCharacter.query.filter_by(
        user_id=current_user.id,
        character_id=people_id
    ).first()

    if favorite is None:
        return jsonify({"msg": "Favorite character not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Character removed from favorites"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
