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

BASE_URL = "/api/shopcarts"


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
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

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

    def test_health(self):
        """It should test health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

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

    def test_get_item_successful_with_query(self):
        """It should get a filtered list of items in a shopcart based on query parameters"""
        shopcart = self._create_shopcarts(1)[0]

        # Create two items using CartItemFactory
        cart_item1 = CartItemFactory(shopcart_id=shopcart.id)
        cart_item2 = CartItemFactory(shopcart_id=shopcart.id)

        # Post the items to the shopcart
        self.client.post(
            f"/api/shopcarts/{shopcart.id}/items", json=cart_item1.serialize()
        )
        self.client.post(
            f"/api/shopcarts/{shopcart.id}/items", json=cart_item2.serialize()
        )

        # Get the list back with a query parameter
        resp = self.client.get(
            f"/api/shopcarts/{shopcart.id}/items?product_id={cart_item1.product_id}"
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], cart_item1.product_id)

    def test_get_items_nonexistent_product_id_query(self):
        """
        It should return an 404 Not Found for a non-existent product_id query
        """
        shopcart = self._create_shopcarts(1)[0]

        # Create two items using CartItemFactory
        cart_item1 = CartItemFactory(shopcart_id=shopcart.id)
        cart_item2 = CartItemFactory(shopcart_id=shopcart.id)

        # Post the items to the shopcart
        self.client.post(f"/shopcarts/{shopcart.id}/items", json=cart_item1.serialize())
        self.client.post(f"/shopcarts/{shopcart.id}/items", json=cart_item2.serialize())

        # Get the list back with a non-existent product_id as a query parameter
        non_existent_product_id = cart_item1.product_id + cart_item2.product_id + 1
        resp = self.client.get(
            f"/shopcarts/{shopcart.id}/items?product_id={non_existent_product_id}"
        )
        self.assertEqual(resp.status_code, 404)

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

    # Test delete multiple items
    def test_delete_items_successfully(self):
        """It should delete multiple items from a shopcart by product_id"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item1 = CartItemFactory()
        cart_item2 = CartItemFactory()
        cart_item1_data = {
            "shopcart_id": cart_item1.shopcart_id,
            "product_id": 2,
            "price": cart_item1.price,
        }
        cart_item2_data = {
            "shopcart_id": cart_item1.shopcart_id,
            "product_id": 3,
            "price": cart_item2.price,
        }
        resp1 = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item1_data,
            content_type="application/json",
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        resp2 = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item2_data,
            content_type="application/json",
        )
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        data = [
            resp1.get_json(),
            resp2.get_json(),
        ]
        logging.debug(data)
        resp = self.client.delete(
            f"{BASE_URL}/{shop_cart.id}/items",
            json={"product_ids": [2, 3]},
            content_type="application/json",
        )

        # Check the status code
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the items are deleted from the database
        for item_data in data:
            product_id = item_data.get("product_id")
            deleted_product = CartItem.find_by_shopcart_id_and_product_id(
                cart_item1.shopcart_id, product_id
            )
            self.assertIsNone(
                deleted_product, f"Product {product_id} should be deleted"
            )

    def test_delete_items_without_existing_product_ids(self):
        """
        It should responds with a 204 status code if the requested product_ids don't exist.
        """
        shopcart_id = 1
        request_data = {"product_ids": [9999999]}
        response = self.client.delete(
            f"/api/shopcarts/{shopcart_id}/items", json=request_data
        )

        # Check that the response status code is 204 (No Content)
        self.assertEqual(response.status_code, 204)

    def test_update_item_shopcart_not_found(self):
        """It should return a 204 NO CONTENT error if updating an item in a missing shopcart"""
        # Create a cart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Try to update with a non-existent shopcart_id
        non_existent_shopcart_id = shop_cart.id + 1
        update_data = {"quantity": 4, "price": 5}
        resp = self.client.put(
            f"/api/shopcarts/{non_existent_shopcart_id}/items/1",
            json=update_data,
            content_type="application/json",
        )

        # Check that the response status code is 204 (No Content)
        self.assertEqual(resp.status_code, 204)

    def test_update_item_product_not_found(self):
        """It should return a 204 NO CONTENT error if the item is not found in the shopcart"""
        # Create a cart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Try to update with a non-existent product_id in a shopcart
        non_existent_product_id = cart_item.product_id + 1
        update_data = {"quantity": 1}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{non_existent_product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    def test_update_item_quantity(self):
        """It should successfully update the quantity of a cart item in a shopcart"""
        # Create a shopcart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Set new quantity
        new_quantity = 99
        # Update the cart item's quantity
        update_data = {"new_quantity": str(new_quantity), "new_price": ""}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        # Check the response message
        data = resp.get_json()
        self.assertEqual(
            data["quantity"], new_quantity, "Failed to update item quantity"
        )

    def test_update_item_price(self):
        """It should successfully update the price of a cart item in a shopcart"""
        # Create a shopcart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Set new price
        new_price = 99.0
        # Update the cart item's price
        update_data = {"new_price": str(new_price), "new_quantity": ""}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        # Check the response message
        data = resp.get_json()
        self.assertEqual(data["price"], new_price, "Failed to update item price")

    def test_update_item_quantity_and_price(self):
        """It should successfully update the quantity and price of a cart item in a shopcart"""
        # Create a shopcart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Set new quantity and price
        new_quantity = 66
        new_price = 99.0
        # Update the cart item's quantity and price
        update_data = {"new_quantity": str(new_quantity), "new_price": str(new_price)}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        # Check the response message
        data = resp.get_json()
        self.assertEqual(data["price"], new_price, "Failed to update item price")
        self.assertEqual(
            data["quantity"], new_quantity, "Failed to update item quantity"
        )

    def test_update_item_quantity_negative_integer(self):
        """It should return a 400 BAD REQUEST response for a negative integer quantity"""
        # Create a shopcart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Update the quantity with a negative integer
        negative_quantity = -1
        update_data = {"new_quantity": str(negative_quantity), "new_price": ""}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        # Check the response
        data = resp.get_json()
        self.assertIn("Quantity must be a positive integer", data["message"])

    def test_update_item_quantity_decimal(self):
        """It should return a 400 BAD REQUEST response for a decimal quantity"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Update the quantity with a decimal value
        decimal_quantity = 0.5
        update_data = {"new_quantity": str(decimal_quantity), "new_price": ""}
        resp = self.client.put(
            f"{BASE_URL}/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        # Check the response
        data = resp.get_json()
        self.assertIn("Quantity must be a positive integer.", data["message"])

    def test_update_item_price_negative(self):
        """It should return a 400 BAD REQUEST response for a negative price"""
        # Create a shopcart and an item in it
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        resp = self.client.post(
            f"/api/shopcarts/{shop_cart.id}/items",
            json=cart_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        # Update the price with a negative number
        negative_price = -5
        update_data = {"new_price": str(negative_price), "new_quantity": ""}
        resp = self.client.put(
            f"/api/shopcarts/{shop_cart.id}/items/{cart_item.product_id}",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        # Check the response
        data = resp.get_json()
        self.assertIn("Price must be a non-negative number.", data["message"])

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

    def test_retrieve_item_success_with_valid_item_and_shopcart(self):
        """It should successfully retrieve an item by ID from an existing shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        cart_item = CartItemFactory()
        self.client.post(f"{BASE_URL}/{shop_cart.id}/items", json=cart_item.serialize())
        resp = self.client.get(
            f"{BASE_URL}/{shop_cart.id}/items/{cart_item.product_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], cart_item.product_id)

    def test_retrieve_item_fails_with_invalid_item_in_valid_shopcart(self):
        """It should return a 404 NOT FOUND for a non-existing item ID in an existing shopcart"""
        shop_cart = self._create_shopcarts(1)[0]
        non_existing_product_id = 99999
        resp = self.client.get(
            f"{BASE_URL}/{shop_cart.id}/items/{non_existing_product_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_item_fails_with_valid_item_in_invalid_shopcart(self):
        """It should return a 404 NOT FOUND for an existing item in a non-existing shopcart"""
        non_existent_shopcart_id = 99999
        cart_item = CartItemFactory()
        resp = self.client.get(
            f"{BASE_URL}/{non_existent_shopcart_id}/items/{cart_item.product_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_item_fails_with_invalid_item_and_shopcart(self):
        """It should return a 404 NOT FOUND for a non-existing item in a non-existing shopcart"""
        non_existent_shopcart_id = 99999
        non_existing_product_id = 88888
        resp = self.client.get(
            f"{BASE_URL}/{non_existent_shopcart_id}/items/{non_existing_product_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
