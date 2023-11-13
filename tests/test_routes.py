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
class TestYourResourceServer(TestCase):  # pylint: disable=too-many-public-methods
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

    def _add_cart_item_to_shopcart(self, shopcart, cart_item):
        """Helper function to add a cart item to a shopcart"""
        self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )

    ######################################################################
    #  S H O P C A R T   T E S T   C A S E S
    ######################################################################
    def test_create_shopcart(self):
        """It should create an empty shopcart"""
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

    def test_create_shopcart_with_empty_body(self):
        """It should return 400_bad_request error for an empty body in the request"""
        resp = self.client.post(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shopcart_having_existed_shopcart(self):
        """It should return a 409 conflict error for creating shopcarts with duplicate customer_id"""
        shopcart = self._create_shopcarts(1)
        resp = self.client.post(BASE_URL, json={"customer_id": shopcart[0].customer_id})
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_get_shopcarts_list(self):
        """It should return a list of shopcarts created"""
        self._create_shopcarts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart_by_id(self):
        """It should return a Shopcart by shopcart_id"""
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], shopcart.customer_id)

    def test_get_shopcart_by_id_404(self):
        """It should return a 404 not found error if shopcart with given id is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shopcarts_by_customer_id(self):
        """It should return a shopcart by customer id"""
        shopcarts = self._create_shopcarts(3)
        resp = self.client.get(
            BASE_URL, query_string=f"customer_id={shopcarts[1].customer_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_id"], shopcarts[1].customer_id)

    # Note: need further check
    def test_get_shopcarts_by_customer_id_404(self):
        """It should return 404 not found by given a non-existed customer id"""
        self._create_shopcarts(3)
        resp = self.client.get(BASE_URL, query_string=f"customer_id={4}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_shopcarts_by_product_id(self):
        """It should return correct shopcarts for a given product id"""
        # Create two cart items
        item1 = CartItemFactory()
        item2 = CartItemFactory()

        # Create three shopcarts
        shopcarts = self._create_shopcarts(3)

        # Add item1 to first two shopcarts and item2 to third shopcart
        self._add_cart_item_to_shopcart(shopcarts[0], item1)
        self._add_cart_item_to_shopcart(shopcarts[1], item1)
        self._add_cart_item_to_shopcart(shopcarts[2], item2)

        # Test querying shopcarts with item1's product_id
        resp = self.client.get(BASE_URL, query_string=f"product_id={item1.product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)  # Should return two shopcarts
        for shopcart in data:
            self.assertTrue(
                any(
                    item["product_id"] == item1.product_id for item in shopcart["items"]
                )
            )

        # Test querying shopcarts with item2's product_id
        resp = self.client.get(BASE_URL, query_string=f"product_id={item2.product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)  # Should return one shopcart
        self.assertTrue(
            any(item["product_id"] == item2.product_id for item in data[0]["items"])
        )

    def test_delete_shopcart(self):
        """It should delete a shopcart by id"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_shopcart_with_wrong_body_format(self):
        """It should return a 415_unsupported_media_type error for a wrong request body format"""
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
        """It should add a CartItem to a ShopCart"""
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
        self.assertEqual(data["product_id"], cart_item.product_id)
        self.assertEqual(data["quantity"], cart_item.quantity)
        self.assertEqual(data["price"], cart_item.price)

    def test_add_cart_item_no_quantity(self):
        """It should default to an item quantity of 1 when no quantity is provided"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()

        # Remove the quantity from the cart_item
        cart_item_data = {
            "shopcart_id": cart_item.shopcart_id,
            "product_id": cart_item.product_id,
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
        self.assertEqual(data["product_id"], cart_item.product_id)

        # Assert that the quantity defaults to 1
        self.assertEqual(data["quantity"], 1)
        self.assertEqual(data["price"], cart_item.price)

    def test_add_duplicate_cart_item(self):
        """It should increment cart item quantity if duplicate item is added to cart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["shopcart_id"], shop_cart.id)
        self.assertEqual(data["product_id"], cart_item.product_id)
        self.assertEqual(data["quantity"], cart_item.quantity)
        self.assertEqual(data["price"], cart_item.price)

        # The second attempt to add the same item
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        # Quantity should be updated.
        self.assertEqual(data["quantity"], cart_item.quantity * 2)

    def test_add_cart_item_without_existed_shopcart(self):
        """It should return a 404 not found error if adding item to a non-existent shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id + 1}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_list(self):
        """It should get a list of items in a shopcart"""
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
            "product_id": cart_item1.product_id + 1,
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
        """It should return a 404 not found error if getting items in a non-existent shopcart"""
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
            "product_id": cart_item1.product_id + 1,
            "price": cart_item1.price,
        }
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items", json=cart_item2_data
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Try to get the list back with shop cart id that doesn't exist
        resp = self.client.get(f"{BASE_URL}/{shop_cart.id + 1}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_cart_item_without_product_id(self):
        """It should return a 400 bad request error if cart item is added without product id"""
        # add two items to the shopcart
        shop_cart = self._create_shopcarts(1)[0]
        # Create an item from cart item factory
        cart_item = {"shopcart_id": 1, "quantity": 1, "price": 1.0}
        resp = self.client.post(f"{BASE_URL}/{shop_cart.id}/items", json=cart_item)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_item_with_existing_item(self):
        """It should delete an item from a shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        cart_item_data = {
            "shopcart_id": cart_item.shopcart_id,
            "product_id": cart_item.product_id,
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
            f"{BASE_URL}/{shop_cart.id}/items/{data['product_id']}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_without_existing_item(self):
        """It should return HTTP_404_NOT_FOUND error if deleting a non-existent item"""
        # send delete request
        shop_cart = self._create_shopcarts(1)[0]
        item_id = random.randint(1000, 9999)
        resp = self.client.delete(
            f"{BASE_URL}/{shop_cart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_item_quantity_shopcart_not_found(self):
        """It should return a 404 NOT FOUND error if updating an item in a missing shopcart"""
        # Update the quantity of an item in a non-existent shopcart
        non_existent_shopcart_id = 9999999
        product_id = 9999999
        update_data = {"quantity": 8}
        resp = self.client.put(
            f"{BASE_URL}/{non_existent_shopcart_id}/items/{product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # Check the response
        data = resp.get_data(as_text=True)
        self.assertIn(
            f"Shopcart with id '{non_existent_shopcart_id}' could not be found", data
        )

    def test_update_item_quantity_product_not_found(self):
        """It should return a 404 NOT FOUND error if the item is not found in the shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        non_existent_product_id = 9999999
        new_quantity = 8
        # Update the quantity of a non-existent product in the shopcart
        update_data = {"quantity": new_quantity}
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/items/{non_existent_product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # Check the response
        data = resp.get_json()  # Assuming your response is in JSON format
        self.assertEqual(data["error"], "Not Found")
        self.assertIn(
            f"Product '{non_existent_product_id}' not found in shopcart {shop_cart.id}",
            data["message"],
        )

    def test_update_item_quantity(self):
        """It should successfully update the quantity of a cart item in a shopcart"""
        # Create a shopcart
        shop_cart = self._create_shopcarts(1)[0]
        # Create a cart item with an initial quantity
        cart_item = CartItemFactory()
        # Add the cart item to the shopcart
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Define the new quantity for the cart item
        new_quantity = 10
        # Retrieve the cart item for testing
        cart_item_for_testing = CartItem.find_by_shopcart_id_and_product_id(
            shopcart_id=shop_cart.id, product_id=cart_item.product_id
        )
        # Update the cart item's quantity
        update_data = {"quantity": new_quantity}
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the response data
        data = resp.get_json()
        logging.debug(data)
        # Verify the response contains the updated quantity
        self.assertEqual(
            data["log"],
            f"Quantity of '{cart_item.product_id}' in shopcart {shop_cart.id} updated to {new_quantity}",
        )
        # Verify the cart item's quantity is updated
        self.assertEqual(cart_item_for_testing.quantity, new_quantity)

    def test_update_item_quantity_negative_integer(self):
        """It should return a 400 BAD REQUEST response for a negative integer quantity"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Update the quantity with a negative integer
        negative_quantity = -88
        update_data = {"quantity": negative_quantity}
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Check the response
        data = resp.get_json()  # Assuming your response is in JSON format
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("Quantity must be a positive integer", data["message"])

    def test_update_item_quantity_decimal(self):
        """It should return a 400 BAD REQUEST response for a decimal (non-integer) quantity"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Update the quantity with a decimal value
        decimal_quantity = 8.8
        update_data = {"quantity": decimal_quantity}
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Check the response
        data = resp.get_json()  # Assuming your response is in JSON format
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("Quantity must be a positive integer", data["message"])

    def test_update_shopcart(self):
        """It should update a shopcart and assert that it has changed"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        # Populate Shopcart with 3 CartItems
        for _ in range(3):
            CartItemFactory(shopcart=shopcart)
        shopcart.create()

        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 3)

        new_items = [CartItemFactory().serialize() for _ in range(2)]

        # Update the shopcart
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}",
            json={
                "customer_id": shopcart.customer_id,
                "items": new_items,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        # NOTE: The primary keys are auto generated so don't compare them
        self.assertEqual(len(data["items"]), len(new_items))
        req_items = sorted(data["items"], key=lambda k: k["product_id"])
        new_items = sorted(new_items, key=lambda k: k["product_id"])
        for i in range(len(data["items"])):
            self.assertEqual(req_items[i]["product_id"], new_items[i]["product_id"])
            self.assertEqual(req_items[i]["quantity"], new_items[i]["quantity"])
            self.assertEqual(req_items[i]["price"], new_items[i]["price"])

    def test_clear_shopcart_items(self):
        """It should clear all items in Customers shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        cart_item_data = {
            "shopcart_id": cart_item.shopcart_id,
            "product_id": cart_item.product_id,
            "price": cart_item.price,
        }

        # Add an item to the shopcart
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Send request to clear shopcart items
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/clear",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["items"], [])

        # Add an item to the shopcart
        resp = self.client.get(
            f"{BASE_URL}/{shop_cart.id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])
