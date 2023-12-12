"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from psycopg.errors import UniqueViolation

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Shopcart.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class DataConflictError(Exception):
    """Used for an data conflict errors when creating"""


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
        try:
            logger.info("Creating %s", self.id)
            self.id = None  # id must be none to generate next primary key
            db.session.add(self)
            db.session.commit()
        except (IntegrityError, DataError) as error:
            if isinstance(error.orig, UniqueViolation):
                # Capture duplicate data error
                raise DataConflictError(
                    "Duplicate Shopcart: Shopcart for customer already exists"
                ) from error

            raise DataValidationError("Invalid Shopcart: " + error.args[0]) from error

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
        return cls.query.all()  # pylint: disable=no-member

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)  # pylint: disable=no-member


######################################################################
#  C A R T I T E M   M O D E L
######################################################################
class CartItem(db.Model, PersistentBase):
    """
    Class that represents an CartItem
    """

    # Table Schema
    # We have a composite primary key of shopcart_id & product_id
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), primary_key=True
    )
    product_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(), nullable=False)

    def __repr__(self):
        return f"<CartItem id=[{self.product_id}] shopcart[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.product_id}: Price={self.price}, Quantity={self.quantity}"

    def create(self):
        """
        Creates a CartItem in the database
        """
        try:
            logger.info("Creating %s", self.product_id)

            # Add extra check to ensure primary keys (product_id & shopcart_id) are present
            if self.product_id is None or self.shopcart_id is None:
                raise DataValidationError(
                    "Invalid CartItem: missing product_id or shopcart_id"
                )
            db.session.add(self)
            db.session.commit()
        except IntegrityError as error:
            raise DataValidationError("Invalid CartItem: " + error.args[0]) from error

    def update(self):
        """
        Updates a CartItem in the database
        """
        logger.info("Updating %s", self.product_id)
        db.session.commit()

    def delete(self):
        """Removes a CartItem from the database"""
        logger.info("Deleting %s", self.product_id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Converts a CartItem into a dictionary"""
        return {
            "shopcart_id": self.shopcart_id,
            "product_id": self.product_id,
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
            self.product_id = data["product_id"]
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

    @classmethod
    def find_by_shopcart_id_and_product_id(cls, shopcart_id, product_id):
        """Returns cart_item in a given shopcart

        Args:
            shopcart_id (Integer): the id of the shopcart you want to match
            product_id (Integer): the id of the product you want to match
        """
        logger.info(
            "Processing lookup for shopcart_id and product_id query for %s and %s ...",
            shopcart_id,
            product_id,
        )
        return cls.query.filter_by(
            shopcart_id=shopcart_id, product_id=product_id
        ).first()


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
    customer_id = db.Column(db.Integer, unique=True, nullable=False)
    items = db.relationship("CartItem", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<ShopCart id=[{self.id}] customer_id=[{self.customer_id}]>"

    def serialize(self):
        """Converts an ShopCart into a dictionary"""
        shopcart = {
            "id": self.id,
            "customer_id": self.customer_id,
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
            self.customer_id = data["customer_id"]
            item_list = data.get("items", [])
            for json_item in item_list:
                item = CartItem()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except (TypeError, AttributeError) as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    def clear_items(self) -> None:
        """
        Deletes all CartItems in the shopcart
        """
        for item in self.items:
            item.delete()

    @classmethod
    def find_shopcart_by_customer_id(cls, customer_id):
        """Returns shopcart with the given customer_id

        Args:
            customer_id (Integer): the id of the customer you want to match
        """
        logger.info("Processing customer id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == int(customer_id))

    @classmethod
    def find_shopcarts_with_product_id(cls, product_id):
        """
        Returns a list of Shopcarts that contain a specific product_id

        Args:
        product_id (int): The product ID to search for
        """
        logger.info(
            "Processing query for shopcarts containing product %s ...", product_id
        )
        # Query the CartItem table for all items with the given product_id
        cart_items = CartItem.query.filter(CartItem.product_id == int(product_id)).all()

        # Extract shopcart_ids from the CartItems
        shopcart_ids = [item.shopcart_id for item in cart_items]

        # Query the Shopcart table for all shopcarts with the extracted shopcart_ids
        shopcarts = cls.query.filter(cls.id.in_(shopcart_ids)).all()
        return shopcarts
