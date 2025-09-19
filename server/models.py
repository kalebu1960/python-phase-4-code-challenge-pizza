from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade='all, delete-orphan')
    
    # add association proxy to get pizzas through restaurant_pizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Keep SerializerMixin but override to_dict
    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurant_pizzas')

    def to_dict(self):
        """Simple to_dict method that only includes basic fields"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

    def to_dict_with_pizzas(self):
        """to_dict method that includes restaurant_pizzas"""
        data = self.to_dict()
        data['restaurant_pizzas'] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return data

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', cascade='all, delete-orphan')
    
    # add association proxy to get restaurants through restaurant_pizzas
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Keep SerializerMixin but override to_dict
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    def to_dict(self):
        """Simple to_dict method that only includes basic fields"""
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Keep SerializerMixin
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # add validation
    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def to_dict(self):
        """to_dict method for RestaurantPizza that includes related data"""
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict() if self.pizza else None,
            'restaurant': self.restaurant.to_dict() if self.restaurant else None
        }

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"