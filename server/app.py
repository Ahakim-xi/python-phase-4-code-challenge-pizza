#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# RESTful resources for tests
from flask import jsonify

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        # Remove 'restaurant_pizzas' from serialization
        return [dict((k, v) for k, v in r.to_dict().items() if k != 'restaurant_pizzas') for r in restaurants], 200

class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(), 200
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        # Remove 'restaurant_pizzas' from serialization
        return [dict((k, v) for k, v in p.to_dict().items() if k != 'restaurant_pizzas') for p in pizzas], 200

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        if not (price and pizza_id and restaurant_id):
            return {"errors": ["validation errors"]}, 400
        try:
            rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(rp)
            db.session.commit()
            result = rp.to_dict()
            result['pizza'] = rp.pizza.to_dict() if rp.pizza else None
            result['restaurant'] = rp.restaurant.to_dict() if rp.restaurant else None
            return result, 201
        except Exception:
            return {"errors": ["validation errors"]}, 400

api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantByIdResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
