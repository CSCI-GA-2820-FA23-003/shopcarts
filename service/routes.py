"""
My Service

ShopCart APIs
- Get all shop carts in the database

"""

from flask import jsonify, request, url_for, make_response, abort
from service.models import CartItem, Shopcart
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/api/health")
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
#  GET SHOPCART BY ID
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>", methods=["GET"])
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


######################################################################
#  CREATE NEW SHOPCART
######################################################################
@app.route("/api/shopcarts", methods=["POST"])
def create_shopcart():
    """
    Creates A SHOPCART FOR A CUSTOMER
    """
    app.logger.info("Request to create a shopcart")
    check_content_type("application/json")

    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())

    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for(
        "get_shopcart_by_id", shopcart_id=shopcart.id, _external=True
    )
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
#  UPDATE EXISTING SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcart(shopcart_id):
    """
    Edit existing shopcart for a customer
    """
    app.logger.info("Request to edit a shopcart")
    check_content_type("application/json")

    shopcart: Shopcart = Shopcart.find(shopcart_id)

    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    shopcart.clear_items()
    shopcart.deserialize(request.get_json())
    shopcart.update()

    message = shopcart.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
#  LIST ALL SHOPCARTS
######################################################################
@app.route("/api/shopcarts")
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
    product_id = request.args.get("product_id")

    # The customer is unique
    if customer_id:
        shopcarts = Shopcart.find_shopcart_by_customer_id(customer_id)
    elif product_id:
        shopcarts = Shopcart.find_shopcarts_with_product_id(product_id)
    else:
        shopcarts = Shopcart.all()
    results = [shopcart.serialize() for shopcart in shopcarts]

    app.logger.info("Return %d shopcart in total.", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
#  DELETE SHOPCART BY ID
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """Delete a shopcart given shopcart id"""
    app.logger.info("Delete the shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.find(shopcart_id)
    # note: if shopcart not exist, do nothing
    if shopcart:
        shopcart.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  CREATE ITEM IN A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items", methods=["POST"])
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

    data = request.get_json()

    if "product_id" not in data:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Field `product_id` missing from request. Could not add item to cart.",
        )

    # Check if 'quantity' is in the data
    if "quantity" not in data:
        data["quantity"] = 1

    # check if the item already exits in the shopcart
    cart_item = CartItem.find_by_shopcart_id_and_product_id(
        shopcart_id, product_id=data["product_id"]
    )

    # If item already exists in cart, increment its quantity
    if cart_item:
        cart_item.quantity += data["quantity"]
        cart_item.update()
        message = cart_item.serialize()
        return make_response(jsonify(message), status.HTTP_201_CREATED)

    # Create an cartItem from the json data
    cart_item = CartItem()
    data["shopcart_id"] = shopcart_id

    cart_item.deserialize(data)

    # Append the item to the shopcart
    shopcart.items.append(cart_item)
    shopcart.update()

    # Prepare a message to return
    message = cart_item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
#  LIST ITEMS IN A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """
    If there is a product_id query parameter, return the queried items for the specified shopcart.
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
    product_id = request.args.get("product_id")

    if product_id:
        # If any product_id does not exist, return a 404
        if not any(item.product_id == int(product_id) for item in items):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with product_id '{product_id}' is not found in Shopcart with shopcart_id '{shopcart_id}'.",
            )
        # Filter items based on the queried product_ids
        items = [item for item in items if item.product_id == int(product_id)]

    # Serialize the filtered items
    results = [item.serialize() for item in items]

    app.logger.info("Return %d items in the shopcart.", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
#  DELETE AN ITEM FROM A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(shopcart_id, item_id):
    """
    Delete an item from a customer shopcart

    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info(
        "Request to delete item %s for shopcart_id: %s", item_id, shopcart_id
    )

    # See if the item exists and delete it if it does
    item = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id=item_id)
    # note: if shopcart not exist, do nothing
    if item:
        item.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  DELETE MULTIPLE PRODUCTS FROM A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items", methods=["DELETE"])
def delete_items(shopcart_id):
    """
    Delete multiple products from a customer shopcart

    This endpoint will delete multiple products based on the list of product IDs provided in the request body
    """
    app.logger.info("Request to delete products for shopcart_id: %s", shopcart_id)

    # The request JSON should include a list of product IDs under the key "product_ids"
    data = request.get_json()
    product_ids = data.get("product_ids", [])

    # Iterate through the list of product IDs and delete each product
    for product_id in product_ids:
        product = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id)
        if product:
            product.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  CLEAR (REMOVE) ALL ITEMS IN A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/clear", methods=["PUT"])
def clear_items_in_cart(shopcart_id):
    """
    Clear items in a customer shopcart

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

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
#  UPDATE AN ITEM IN A SHOPCART
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["PUT"])
def update_items(shopcart_id, product_id):
    """
    Update an item in the shopcart quantitatively
    """
    app.logger.info(
        "Request to update item quantity with shopcart_id: %s, and product_id: %s",
        shopcart_id,
        product_id,
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
    cart_item = CartItem.find_by_shopcart_id_and_product_id(shopcart_id, product_id)

    if not cart_item:
        # Return a 404 response if the product is not found in the shopcart
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product '{product_id}' not found in shopcart {shopcart_id}",
        )

    # Get new quantity from the request JSON
    request_data = request.get_json()
    new_quantity = request_data.get("quantity")

    if new_quantity is None:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Quantity must be a positive integer.",
        )

    if not isinstance(new_quantity, int) or new_quantity <= 0:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Quantity must be a positive integer.",
        )

    # Update the quantity
    cart_item.quantity = new_quantity
    cart_item.update()

    return make_response(
        jsonify(
            {
                "log": f"Quantity of '{product_id}' in shopcart {shopcart_id} updated to {new_quantity}"
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  GET AN ITEM FROM A SHOPCART BY ID
######################################################################
@app.route("/api/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["GET"])
def get_cart_item(shopcart_id, product_id):
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
    return make_response(jsonify(cart_item.serialize()), status.HTTP_200_OK)


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
