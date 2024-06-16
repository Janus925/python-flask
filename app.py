import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    making_time = db.Column(db.String(50), nullable=False)
    serves = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'making_time': self.making_time,
            'serves': self.serves,
            'ingredients': self.ingredients,
            'cost': self.cost
        }


@app.route('/recipes', methods=['POST'])
def create_recipe():
    data = request.get_json()
    required_fields = ['title', 'making_time', 'serves', 'ingredients', 'cost']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Recipe creation failed!", "required": "title, making_time, serves, ingredients, cost"}), 200
    
    new_recipe = Recipes(
        title=data['title'],
        making_time=data['making_time'],
        serves=data['serves'],
        ingredients=data['ingredients'],
        cost=data['cost']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message": "Recipe successfully created!", "recipe": [new_recipe.serialize()]}), 200

@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipes.query.all()
    return jsonify({"recipes": [recipe.serialize() for recipe in recipes]}), 200

@app.route('/recipes/<int:id>', methods=['GET'])
def get_recipe(id):
    recipe = Recipes.query.get(id)
    if not recipe:
        return jsonify({"message": "No recipe found"}), 404
    return jsonify({"message": "Recipe details by id", "recipe": [recipe.serialize()]}), 200

@app.route('/recipes/<int:id>', methods=['PATCH'])
def update_recipe(id):
    recipe = Recipes.query.get(id)
    if not recipe:
        return jsonify({"message": "No recipe found"}), 404
    
    data = request.get_json()
    for key in data:
        if hasattr(recipe, key):
            setattr(recipe, key, data[key])
    db.session.commit()
    return jsonify({"message": "Recipe successfully updated!", "recipe": [recipe.serialize()]}), 200

@app.route('/recipes/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe = Recipes.query.get(id)
    if not recipe:
        return jsonify({"message": "No recipe found"}), 404
    
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe successfully removed!"}), 200

if __name__ == '__main__':
    app.run(debug=True)