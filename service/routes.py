"""
Shopcart API Service with Swagger
"""

from flask import jsonify, request, abort
from flask_restx import Resource, fields, reqparse
from service.models import CartItem, Shopcart
from service.common import status  # HTTP Status Codes
from . import app, api  # Import Flask application


######################################################################
# [Models]:
######################################################################
cartItem_model = api.model(
    "CartItem",
    {
        "product_id": fields.Integer(required=True, description="The id of the item"),
        "shopcart_id": fields.Integer(
            required=True, description="The id of the shopcart that contains the item"
        ),
        "price": fields.Float(required=True, description="The price of the item"),
        "quantity": fields.Integer(
            required=True, description="The quantity of the item"
        ),
    },
)

create_shopcart_model = api.model(
    "Shopcart",
    {
        "customer_id": fields.Integer(
            required=True, description="The customer id related to the shopcart"
        ),
        "items": fields.List(
            fields.Nested(cartItem_model),
            required=True,
            description="The items in the shopcart",
        ),
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    create_shopcart_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="List Shopcarts by product id",
)
shopcart_args.add_argument(
    "customer_id",
    type=int,
    location="args",
    required=False,
    help="List Shopcarts by customer id",
)

cartItem_args = reqparse.RequestParser()
cartItem_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="Filter items by product_id",
)


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  PATH: /api/shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """
    Allows the manipulation of multiple shopcarts
    """

    ######################################################################
    #  CREATE NEW SHOPCART
    ######################################################################
    @api.doc("create_shopcarts")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Creates A SHOPCART FOR A CUSTOMER
        """
        app.logger.info("Request to create a shopcart")
        check_content_type("application/json")

        shopcart = Shopcart()
        shopcart.deserialize(api.payload)
        shopcart.create()

        # Create a message to return
        message = shopcart.serialize()
        location_url = api.url_for(
            ShopcartResource, shopcart_id=shopcart.id, _external=True
        )

        return message, status.HTTP_201_CREATED, {"Location": location_url}

    ######################################################################
    #  LIST ALL SHOPCARTS
    ######################################################################
    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.response(404, "No shopcart found")
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """
        If there is shopcart query, return the queried shopcart
        else return all shopcarts

        return: a list of shopcarts in the DB
        """
        app.logger.info("Get all shopcarts in database.")

        shopcarts = []

        # process the query string if any
        args = shopcart_args.parse_args()
        customer_id = args["customer_id"]
        product_id = args["product_id"]

        # The customer is unique
        if customer_id:
            shopcarts = Shopcart.find_shopcart_by_customer_id(customer_id)
        elif product_id:
            shopcarts = Shopcart.find_shopcarts_with_product_id(product_id)
        else:
            shopcarts = Shopcart.all()

        results = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info(results)
        app.logger.info("Return %d shopcart in total.", len(results))
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /api/shopcarts/<int:shopcart_id>
######################################################################
@api.route("/shopcarts/<int:shopcart_id>", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """
    Allows the manipulation of a single Shopcart
    """

    ######################################################################
    #  GET A SHOPCART BY ID
    ######################################################################
    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a shopcart given a shopcart id
        """
        app.logger.info("Request for Shopcart with id: %s", shopcart_id)

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"404 Not Found. Shopcart with id '{shopcart_id}' could not be found.",
            )

        return shopcart.serialize(), status.HTTP_200_OK

    ######################################################################
    #  UPDATE AN EXISTING SHOPCART
    ######################################################################
    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a shopcart given a shopcart id, with request JSON
        """
        app.logger.info("Request to edit a shopcart")
        check_content_type("application/json")

        data = api.payload
        shopcart = Shopcart.find(shopcart_id)

        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        shopcart.clear_items()
        shopcart.deserialize(data)
        shopcart.update()

        message = shopcart.serialize()
        return message, status.HTTP_200_OK

    ######################################################################
    #  DELETE A SHOPCART BY ID
    ######################################################################
    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a shopcart given a shopcart id.
        """
        app.logger.info("Delete the shopcart with id: %s", shopcart_id)

        shopcart = Shopcart.find(shopcart_id)
        # note: if shopcart not exist, do nothing
        if shopcart:
            for item in shopcart.items:
                item.delete()
            shopcart.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /api/shopcarts/<int:shopcart_id>/items
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """
    Allows the manipulation of multiple items in a shopcart
    """

    ######################################################################
    #  CREATE ITEM IN A SHOPCART
    ######################################################################
    @api.doc("create_cart_items")
    @api.response(400, "The posted data was not valid")
    @api.expect(cartItem_model)
    @api.marshal_with(cartItem_model, code=201)
    def post(self, shopcart_id):
        """
        Create an item in an Shopcart

        This endpoint will add an item to the shopcart
        """
        app.logger.info(
            "Request to create the item in the shopcart with id: %s", shopcart_id
        )
        check_content_type("application/json")

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        data = api.payload

        if "product_id" not in data:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Field `product_id` missing from request. Could not add item to cart.",
            )

        # Check if 'quantity' is in the data
        if "quantity" not in data:
            data["quantity"] = 1

        # Check if the item already exits in the shopcart
        product_id = data["product_id"]
        cart_item = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id)

        # If item already exists in cart, increment its quantity
        if cart_item:
            cart_item.quantity += data["quantity"]
            cart_item.update()
            message = cart_item.serialize()
        else:
            # Create a new CartItem from the json data
            cart_item = CartItem()
            data["shopcart_id"] = shopcart_id
            cart_item.deserialize(data)

            # Append the item to the shopcart
            shopcart.items.append(cart_item)
            shopcart.update()

            # Prepare a message to return
            message = cart_item.serialize()

        location_url = api.url_for(
            ShopcartResource, shopcart_id=shopcart.id, _external=True
        )
        app.logger.info(
            "Item [%s] has been added to the shopcart [%s]",
            cart_item.product_id,
            shopcart_id,
        )

        return message, status.HTTP_201_CREATED, {"Location": location_url}

    ######################################################################
    #  LIST ITEMS IN A SHOPCART
    ######################################################################
    @api.doc("list_cart_items")
    @api.response(404, "items not found")
    @api.expect(cartItem_args)
    @api.marshal_list_with(cartItem_model)
    def get(self, shopcart_id):
        """
        If there is a product_id query parameter,
        return the queried items for the specified shopcart.
        Else return all items for the specified shopcart.

        return: a list of items in the specified shopcart
        """
        app.logger.info("Request for cart items for Shopcart with id: %s", shopcart_id)

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        # Get the list of items from the shopcart
        items = shopcart.items

        # Process query parameters if any
        args = cartItem_args.parse_args()
        product_id = args.get("product_id")

        if product_id:
            # If any product_id does not exist, return a 404
            if not any(item.product_id == int(product_id) for item in items):
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Item with product_id '{product_id}' is not found "
                    + f"in Shopcart with shopcart_id '{shopcart_id}'.",
                )
            # Filter items based on the queried product_ids
            items = [item for item in items if item.product_id == int(product_id)]

        # Serialize the filtered items
        results = [item.serialize() for item in items]

        app.logger.info("Return %d items in the shopcart.", len(results))
        return results, status.HTTP_200_OK

    ######################################################################
    #  DELETE ITEMS FROM A SHOPCART
    ######################################################################
    @api.doc("delete_cart_items")
    @api.response(204, "Products deleted successfully")
    @api.response(404, "Item not found for deletion")
    @api.expect(cartItem_args)
    def delete(self, shopcart_id):
        """
        Delete multiple products from a customer shopcart

        This endpoint will delete multiple products based on the list of
        product IDs provided in the request body
        """
        app.logger.info("Request to delete products for shopcart_id: %s", shopcart_id)

        # Parse the request JSON using the defined parser
        args = cartItem_args.parse_args()
        product_ids = args.get("product_ids", [])

        # Iterate through the list of product IDs and delete each product
        for product_id in product_ids:
            product = CartItem.find_by_shopcart_id_and_product_id(
                shopcart_id, product_id
            )
            if product:
                product.delete()
            else:
                # If any product_id does not exist, return a 404
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Item with product_id '{product_id}' is not found "
                    + f"in Shopcart with shopcart_id '{shopcart_id}'.",
                )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /api/shopcarts/<int:shopcart_id>/items/<int:product_id>
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("product_id", "The Item identifier")
class ItemResource(Resource):
    """
    Allows the manipulation of a single item in a shopcart
    """

    ######################################################################
    #  GET AN ITEM FROM A SHOPCART BY ID
    ######################################################################
    @api.doc("get_cart_item")
    @api.response(404, "Item not found")
    @api.marshal_with(cartItem_model)
    def get(self, shopcart_id, product_id):
        """
        Retrieve a specific item from a shopcart by product ID.

        This endpoint returns the details of a specific item in a given shopcart.
        If the item or shopcart does not exist, it returns a 404 Not Found.
        """
        app.logger.info(
            "Request to get item with product_id: %s from shopcart_id: %s",
            product_id,
            shopcart_id,
        )

        # Check if the shopcart exists
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        # Locate the product in the shopcart
        cart_item = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id)
        if not cart_item:
            # Return a 404 response if the product is not found in the shopcart
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' not found in shopcart {shopcart_id}",
            )

        # Return the item details
        return cart_item.serialize(), status.HTTP_200_OK

    ######################################################################
    #  UPDATE AN ITEM IN A SHOPCART BY ID
    ######################################################################
    @api.doc("update_items")
    @api.response(404, "Shopcart not found")
    @api.response(204, "Item not found in the shopcart")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(cartItem_model)
    @api.marshal_with(cartItem_model)
    def put(self, shopcart_id, product_id):
        """
        Update the quantity and/or the price of an item in the shopcart
        """
        app.logger.info(
            "Request to update item quantity and/or price with shopcart_id: %s, and product_id: %s",
            shopcart_id,
            product_id,
        )
        check_content_type("application/json")

        # Check if the shopcart exists; abort and return 204 if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            # Return a 204 response if the shopcart is not found
            return "", status.HTTP_204_NO_CONTENT

        # Locate the product in the shopcart
        cart_item = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id)

        if not cart_item:
            # Return a 204 response if the product is not found in the shopcart
            return "", status.HTTP_204_NO_CONTENT

        # Parse the request data using the defined parser
        data = api.payload
        new_quantity = data.get("new_quantity", None)
        new_price = data.get("new_price", None)
        # If no information is provided, return 400
        if new_quantity is None and new_price is None:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Either quantity or price must be provided.",
            )

        # If only new quantity is provided,
        if new_quantity is not None and new_quantity != "":
            # Update the quantity and provide message
            new_quantity = validate_quantity(new_quantity)
            cart_item.quantity = new_quantity

        # If only new price is provided,
        if new_price is not None and new_price != "":
            # Update the price and provide message
            new_price = validate_price(new_price)
            cart_item.price = new_price

        # Update the item information and return
        cart_item.update()
        return (
            cart_item.serialize(),
            status.HTTP_200_OK,
        )

    ######################################################################
    #  DELETE AN ITEM FROM A SHOPCART
    ######################################################################
    @api.doc("delete_item")
    @api.response(204, "Item deleted")
    @api.response(404, "Item not found for deletion")
    def delete(self, shopcart_id, product_id):
        """
        Delete an item from a customer shopcart

        This endpoint will delete an item based the id specified in the path
        """
        app.logger.info(
            "Request to delete item %s for shopcart_id: %s", product_id, shopcart_id
        )

        # See if the item exists and delete it if it does
        item = CartItem.find_by_shopcart_id_and_product_id(
            shopcart_id, product_id=product_id
        )
        # note: if shopcart not exist, do nothing
        if item:
            item.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /api/shopcarts/<int:shopcart_id>/clear
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/clear", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ClearItemsInCart(Resource):
    """
    Allows the clearing of all items in a shopcart
    """

    ######################################################################
    #  CLEAR (REMOVE) ALL ITEMS IN A SHOPCART
    ######################################################################
    @api.doc("clear_items_in_cart")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Clear all items in a customer shopcart

        This endpoint will delete all items in the shopcart specified in the path
        """
        app.logger.info("Request to clear items for shopcart_id: %s", shopcart_id)

        # Check if the shopcart exists and abort if it doesn't (Same as in create_items)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        for item in shopcart.items:
            item.delete()

        return shopcart.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )


def validate_quantity(new_quantity):
    """Check if quantity is a positive integer"""
    try:
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            raise ValueError
    except ValueError:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Quantity must be a positive integer.",
        )
    return new_quantity


def validate_price(new_price):
    """Check if price is a non-negative number"""
    try:
        new_price = float(new_price)
        if new_price < 0:
            raise ValueError
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, "Price must be a non-negative number.")
    return new_price
