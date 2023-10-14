"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, make_response
from service.common import status  # HTTP Status Codes
from service.models import Shopcart

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...

######################################################################
# CREATE A SHOPCART FOR A CUSTOMER
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["POST"])
def create_shopcart(customer_id):
    """
    Creates A SHOPCART FOR A CUSTOMER
    """
    app.logger.info("Request to create a shopcart")

    shopcart = Shopcart()
    
    shopcart.customer_id = customer_id
    
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("create_shopcart", customer_id=customer_id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )