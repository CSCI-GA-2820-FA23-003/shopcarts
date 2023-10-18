"""
My Service

ShopCart APIs 
- Get all shop carts in the database

"""

from flask import jsonify, request, url_for, make_response, abort
from service.models import CartItem, Shopcart
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Shopcart REST API Service",
            version="1.0",
            paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  SHOPCART   A P I   E N D P O I N T S
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcart_by_id(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts", methods=["POST"])
def create_shopcart():
    """
    Creates A SHOPCART FOR A CUSTOMER
    """
    app.logger.info("Request to create a shopcart")
    check_content_type("application/json")

    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())

    # check if no customer_id passing in the body
    if not request.get_json()["customer_id"]:
        return make_response(
            "Missing customer_id in request body.", status.HTTP_400_BAD_REQUEST
        )

    # check if the customer already have a shopcart
    shopcarts = Shopcart.find_shopcart_by_customer_id(request.get_json()["customer_id"])
    results = [shopcart.serialize() for shopcart in shopcarts]
    if len(results) > 0:
        return make_response(
            "Customer already have a shopcart", status.HTTP_400_BAD_REQUEST
        )

    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for(
        "create_shopcart", customer_id=shopcart.customer_id, _external=True
    )
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


@app.route("/shopcarts")
def list_shopcarts():
    """
    If there is shopcart query, return the queried shopcart
    else return all shopcarts

    return: a list of shopcarts in the DB
    """
    app.logger.info("Get all shopcarts in database.")

    shopcarts = []

    # process the query string if any
    customer_id = request.args.get("customer_id")
    if customer_id:
        shopcarts = Shopcart.find_shopcart_by_customer_id(customer_id)
    else:
        shopcarts = Shopcart.all()
    results = [shopcart.serialize() for shopcart in shopcarts]

    app.logger.info("Return %d shopcart in total.", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """Delete a shopcart given shopcart id"""
    app.logger.info("Delete the shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.find(shopcart_id)
    # note: if shopcart not exist, do nothing
    if shopcart:
        shopcart.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  C A R T  I T E M   A P I   E N D P O I N T S
######################################################################


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """
    Create an item on an Shopcart

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

    # check if the item already exits in the shopcart
    cart_items = CartItem.find_cart_item_by_shopcart_id_and_product_name(
        shopcart_id, request.get_json()["product_name"]
    )

    results = [cart_item.serialize() for cart_item in cart_items]
    if len(results) > 0:
        return make_response(
            "Cart item already exists in the shopcart", status.HTTP_400_BAD_REQUEST
        )
    # Create an cartItem from the json data
    cart_item = CartItem()
    data = request.get_json()

    # Check if 'quantity' is in the data
    if "quantity" not in data:
        data["quantity"] = 1

    cart_item.deserialize(request.get_json())

    # Append the item to the shopcart
    shopcart.items.append(cart_item)
    shopcart.update()

    # Prepare a message to return
    message = cart_item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """Returns all of the cart items for a Shopcart"""
    app.logger.info("Request for all cart items for Shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Get the list of cart items from the shopcart
    results = [item.serialize() for item in shopcart.items]

    return make_response(jsonify(results), status.HTTP_200_OK)

@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(shopcart_id, item_id):
    """
    Delete an item from a customer shopcart

    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete item %s for shopcart_id: %s", item_id, shopcart_id)

    # See if the item exists and delete it if it does
    item = CartItem.find(item_id)
    # note: if shopcart not exist, do nothing
    if item:
        item.delete()
    else:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )
    return make_response("", status.HTTP_204_NO_CONTENT)

# UPDATE AN EXISTING ITEM'S QUANTITY
@app.route("/shopcarts/<int:shopcart_id>/items/<string:product_name>", methods=["PUT"])
def update_items(shopcart_id, product_name):
    """
    Update an item in the shopcart quantitatively
    """
    app.logger.info(
        "Request to update item quantity with shopcart_id: %s, and product_name: %s",
        shopcart_id,
        product_name,
    )
    check_content_type("application/json")

    # Check if the shopcart exists and abort if it doesn't (Same as in create_items)
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Locate the product in the shopcart
    cart_items = CartItem.find_cart_item_by_shopcart_id_and_product_name(
        shopcart_id, product_name
    )

    if not cart_items:
        # Return a 404 response if the product is not found in the shopcart
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product '{product_name}' not found in shopcart {shopcart_id}",
        )

    # Get new quantity from the request JSON
    request_data = request.get_json()
    new_quantity = request_data.get("quantity")

    if new_quantity is not None:
        # Check if the new quantity is a positive integer
        if not isinstance(new_quantity, int) or new_quantity <= 0:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Quantity must be a positive integer.",
            )
        # Update the quantity
        cart_item = cart_items[0]
        cart_item.quantity = new_quantity
        cart_item.update()

        return make_response(
            jsonify(
                {
                    "log": f"Quantity of '{product_name}' in shopcart {shopcart_id} updated to {new_quantity}"
                }
            ),
            status.HTTP_200_OK,
        )


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
