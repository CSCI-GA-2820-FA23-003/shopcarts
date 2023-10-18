"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import random
import logging
from unittest import TestCase
from tests.factories import ShopcartFactory, CartItemFactory
from service import app
from service.models import db, Shopcart, CartItem, init_db
from service.common import status  # HTTP Status Codes

# DATABASE_URI = os.getenv(
#     "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
# )

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_shopcarts(self, count):
        """Create a shopcart"""
        shopcarts = []
        for _ in range(count):
            shopcart = ShopcartFactory()
            resp = self.client.post(BASE_URL, json=shopcart.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcarts.append(shopcart)
        return shopcarts

    ######################################################################
    #  S H O P C A R T   T E S T   C A S E S
    ######################################################################
    def test_create_shopcart(self):
        """It should Create a empty shopcart"""
        customer_id = random.randint(1000, 9999)
        resp = self.client.post(
            BASE_URL, json={"customer_id": customer_id, "items": []}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["customer_id"], customer_id, "customer_id does not match"
        )
        self.assertEqual(new_shopcart["items"], [], "Items does not match")

    def test_create_shopcart_with_wrong_body_format(self):
        """It should get a 415 bad request response"""
        resp = self.client.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_with_empty_body(self):
        """It should get a 400 bad request response"""
        resp = self.client.post(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shopcart_having_existed_shopcart(self):
        """It should get a 400 bad request response"""
        shopcart = self._create_shopcarts(1)
        resp = self.client.post(BASE_URL, json={"customer_id": shopcart[0].customer_id})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_shopcarts_list(self):
        """It should get a list of shopcarts created"""
        self._create_shopcarts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart_by_id(self):
        """It should Get a Shopcart by shopcart_id"""
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], shopcart.customer_id)

    def test_get_shopcart_by_id_404(self):
        """It should return a 404 error if shopcart with given id is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shopcarts_by_customer_id(self):
        """It should Get a shopcart by customer id"""
        shopcarts = self._create_shopcarts(3)
        resp = self.client.get(
            BASE_URL, query_string=f"customer_id={shopcarts[1].customer_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_id"], shopcarts[1].customer_id)

    # Note: need further check
    def test_get_shopcarts_by_customer_id_404NotFound(self):
        """It should return 404 not found by given a non-existed customer id"""
        shopcarts = self._create_shopcarts(3)
        resp = self.client.get(BASE_URL, query_string=f"customer_id={4}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_shopcart(self):
        """It should delete a shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  C A R T   I T E M   T E S T   C A S E S
    ######################################################################

    def test_add_cart_item(self):
        """It should Add an cart item to a shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shop_cart.id)
        self.assertEqual(data["product_name"], cart_item.product_name)
        self.assertEqual(data["quantity"], cart_item.quantity)
        self.assertEqual(data["price"], cart_item.price)

    def test_add_cart_item_no_quantity(self):
        """It should default to a quantity of 1 when no quantity is provided"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()

        # Remove the quantity from the cart_item
        cart_item_data = {
            "shopcart_id": cart_item.shopcart_id,
            "product_name": cart_item.product_name,
            "price": cart_item.price,
        }

        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shop_cart.id)
        self.assertEqual(data["product_name"], cart_item.product_name)

        # Assert that the quantity defaults to 1
        self.assertEqual(data["quantity"], 1)
        self.assertEqual(data["price"], cart_item.price)

    def test_add_cart_item_having_existed_item(self):
        """It should get a 400 bad request response"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shop_cart.id)
        self.assertEqual(data["product_name"], cart_item.product_name)
        self.assertEqual(data["quantity"], cart_item.quantity)
        self.assertEqual(data["price"], cart_item.price)

        # The second attempt to add the same item
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_cart_item_without_existed_shopcart(self):
        """It should get a 404 not found response"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id + 1}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_list(self):
        """It should Get a list of items"""
        # add two items to the shopcart
        shop_cart = self._create_shopcarts(1)[0]

        # Create an item from cart item factory
        cart_item1 = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items", json=cart_item1.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create the second item by modifying the first one to ensure their difference
        cart_item2_data = {
            "shopcart_id": cart_item1.shopcart_id,
            "product_name": cart_item1.product_name + "No.2",
            "price": cart_item1.price,
        }
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items", json=cart_item2_data
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{shop_cart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_item_list_without_existed_shopcart(self):
        """It should get a 404 not found response"""
        # add two items to the shopcart
        shop_cart = self._create_shopcarts(1)[0]

        # Create an item from cart item factory
        cart_item1 = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items", json=cart_item1.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create the second item by modifying the first one to ensure their difference
        cart_item2_data = {
            "shopcart_id": cart_item1.shopcart_id,
            "product_name": cart_item1.product_name + "No.2",
            "price": cart_item1.price,
        }
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items", json=cart_item2_data
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Try to get the list back with shop cart id that doesn't exist
        resp = self.client.get(f"{BASE_URL}/{shop_cart.id + 1}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_with_existing_item(self):
        """It should Delete an item from a customers shopcart"""        
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        cart_item_data = {
            "shopcart_id": cart_item.shopcart_id,
            "product_name": cart_item.product_name,
            "price": cart_item.price,
        }

        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{shop_cart.id}/items/{data['id']}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_item_without_existing_item(self):
        """It should return HTTP_404_NOT_FOUND"""
        # send delete request
        shop_cart = self._create_shopcarts(1)[0]
        item_id = random.randint(1000, 9999)
        resp = self.client.delete(
            f"{BASE_URL}/{shop_cart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)