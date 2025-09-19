from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# Add the route implementations
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        # Use the simple to_dict method that excludes restaurant_pizzas
        return [restaurant.to_dict() for restaurant in restaurants]


class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        # Use the to_dict_with_pizzas method for single restaurant endpoint
        return restaurant.to_dict_with_pizzas()
    
    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        # Use the simple to_dict method that excludes restaurant_pizzas
        return [pizza.to_dict() for pizza in pizzas]


class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')
            
            # Check if pizza and restaurant exist
            pizza = db.session.get(Pizza, pizza_id)
            restaurant = db.session.get(Restaurant, restaurant_id)
            
            if not pizza or not restaurant:
                return {'errors': ['Pizza or Restaurant not found']}, 404
            
            # Validate price
            if not 1 <= price <= 30:
                return {'errors': ['validation errors']}, 400  # Change this line
            
            # Create new RestaurantPizza
            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            return restaurant_pizza.to_dict(), 201
            
        except Exception as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400  # And this line


# Register the routes with the API
api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantByIdResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)