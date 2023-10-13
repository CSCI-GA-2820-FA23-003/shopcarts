"""
My Service

ShopCart APIs 
- Get all shop carts in the database

"""

from flask import jsonify, request, url_for, make_response, abort
from service.models import CartItem, Shopcart
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
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
        shopcarts = Shopcart.find_by_customer_id(customer_id)
    else:
        shopcarts = Shopcart.all()
    results = [shopcarts.serialize() for shopcart in shopcarts]

    app.logger.info("Return %d shopcart in total.", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
#  CARTITEM   A P I   E N D P O I N T S
######################################################################
