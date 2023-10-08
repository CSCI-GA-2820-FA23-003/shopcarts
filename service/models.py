"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Shopcart.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self):
        """
        Creates a Shopcart to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Shopcart to the database
        """
        logger.info("Updating %s", self.id)
        db.session.commit()

    def delete(self):
        """Removes a Shopcart from the data store"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  I T E M   M O D E L
######################################################################
class CartItem(db.Model, PersistentBase):
    """
    Class that represents an CartItem
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), nullable=False
    )
    product_name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float())

    def __repr__(self):
        return f"<CartItem {self.product_name} id=[{self.id}] shopcart[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.product_name}: Price={self.price}, Quantity={self.quantity}"

    def serialize(self) -> dict:
        """Converts a CartItem into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates a CartItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.product_name = data["product_name"]
            self.price = data["price"]
            self.quantity = data["quantity"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid CartItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid CartItem: body of request contained "
                "bad or no data " + error.args[0]
            ) from error
        return self


######################################################################
#  S H O P C A R T   M O D E L
######################################################################
class Shopcart(db.Model, PersistentBase):
    """
    Class that represents an ShopCart
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship("CartItem", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<ShopCart id=[{self.id}]>"

    def serialize(self):
        """Converts an ShopCart into a dictionary"""
        shopcart = {
            "id": self.id,
            "items": [],
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates an ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = CartItem()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        except AttributeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained "
                "bad or no attribute - " + error.args[0]
            ) from error
        return self
