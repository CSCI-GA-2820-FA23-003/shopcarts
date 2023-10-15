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
@app. route("/shopcarts", methods= ["POST"]) 
def create_shopcart():
    """
    Creates A SHOPCART FOR A CUSTOMER
    """
    app.logger.info ("Request to create a shopcart") 
    check_content_type("application/json")

    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())

    # check if no customer_id passing in the body
    if not request.get_json()['customer_id']:
        return make_response("Missing customer_id in request body.", status.HTTP_400_BAD_REQUEST)

    # check if the customer already have a shopcart
    shopcarts = Shopcart.find_shopcart_by_customer_id(request.get_json()['customer_id'])
    results = [shopcart.serialize() for shopcart in shopcarts]
    if len(results) > 0:
        return make_response("Customer already have a shopcart", status.HTTP_400_BAD_REQUEST)

    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for(
        "create_shopcart", customer_id=shopcart.customer_id, _external=True
    )
    return make_response (
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

@app.route("/shopcarts")
def list_shopcarts():
    """
    If there is shopcart query, return the queried shopcart
    else return all shopcarts

    return: a list of shopcarts in the DB
    """
    app.logger.info("Get all shopcats exsited in database.")

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


######################################################################
#  CARTITEM   A P I   E N D P O I N T S
######################################################################

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