"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from service import app
from service.models import Shopcart, CartItem, DataValidationError, db
from tests.factories import ShopcartFactory, CartItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcart(unittest.TestCase):
    """Test Cases for YourResourceModel Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(CartItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """It should Create a Shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        shopcart = Shopcart(items=fake_shopcart.items)
        self.assertIsNotNone(shopcart)
        self.assertEqual(shopcart.id, None)

    def test_add_a_shopcart(self):
        """It should Create a Shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        shopcart.create()
        # # Assert that it was assigned an ID and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

    def test_add_with_error_duplicate_customer_id(self):
        """It should Raise an error if duplicate customer ID is used"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        shopcart.create()
        shopcart2 = ShopcartFactory()
        shopcart2.customer_id = shopcart.customer_id
        self.assertRaises(DataValidationError, shopcart2.create)

    def test_read_shopcart(self):
        """It should Read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Read it back
        found_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.items, [])

    def test_delete_a_shopcart(self):
        """It should Delete a shopcart from the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        # Assert that deleted shopcart is no longer in the database
        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)

    def test_list_all_shopcarts(self):
        """It should List all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for shopcart in ShopcartFactory.create_batch(5):
            shopcart.create()
        # Assert that there are now 5 shopcarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_find_shopcart_by_id(self):
        """It should Find a Shopcart by id"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Fetch it back by id
        found_shopcart = Shopcart.find(shopcart.id)
        self.assertIsNotNone(found_shopcart)
        self.assertEqual(found_shopcart.id, shopcart.id)

    def test_serialize_a_shopcart(self):
        """It should Serialize a Shopcart"""
        shopcart = ShopcartFactory()
        cart_item = CartItemFactory()
        shopcart.items.append(cart_item)
        serialized_shopcart = shopcart.serialize()
        self.assertEqual(serialized_shopcart["id"], shopcart.id)
        self.assertEqual(len(serialized_shopcart["items"]), 1)
        items = serialized_shopcart["items"]
        self.assertEqual(items[0]["id"], cart_item.id)
        self.assertEqual(items[0]["shopcart_id"], cart_item.shopcart_id)
        self.assertEqual(items[0]["product_name"], cart_item.product_name)
        self.assertEqual(items[0]["quantity"], cart_item.quantity)
        self.assertEqual(items[0]["price"], cart_item.price)

    def test_deserialize_a_shopcart(self):
        """It should Deserialize a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.items.append(CartItemFactory())
        shopcart.create()
        serialized_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serialized_shopcart)
        self.assertEqual(len(new_shopcart.items), len(shopcart.items))
        self.assertEqual(
            new_shopcart.items[0].shopcart_id, shopcart.items[0].shopcart_id
        )
        self.assertEqual(new_shopcart.items[0].price, shopcart.items[0].price)
        self.assertEqual(new_shopcart.items[0].quantity, shopcart.items[0].quantity)
        self.assertEqual(
            new_shopcart.items[0].product_name, shopcart.items[0].product_name
        )

    def test_deserialize_cart_item(self):
        """It should Deserialize a Cart Item"""
        cart_item = CartItemFactory()
        cart_item.create()
        serialized_cart_item = cart_item.serialize()
        new_cart_item = CartItem()
        new_cart_item.deserialize(serialized_cart_item)
        self.assertEqual(new_cart_item.shopcart_id, cart_item.shopcart_id)
        self.assertEqual(new_cart_item.product_name, cart_item.product_name)
        self.assertEqual(new_cart_item.quantity, cart_item.quantity)
        self.assertEqual(new_cart_item.price, cart_item.price)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a Shopcart with a KeyError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_with_attribute_error(self):
        """It should not Deserialize an Shopcart with a TypeError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

    def test_deserialize_cart_item_key_error(self):
        """It should not Deserialize a CartItem with a KeyError"""
        cart_item = CartItem()
        self.assertRaises(DataValidationError, cart_item.deserialize, {})

    def test_deserialize_cart_item_type_error(self):
        """It should not Deserialize a CartItem with a TypeError"""
        cart_item = CartItem()
        self.assertRaises(DataValidationError, cart_item.deserialize, [])

    def test_add_shopcart_and_item(self):
        """It should Create a Shopcart with a CartItem and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        cart_item = CartItemFactory(shopcart=shopcart)
        shopcart.items.append(cart_item)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(new_shopcart.items[0].product_name, cart_item.product_name)

        cart_item2 = CartItemFactory(shopcart=shopcart)
        shopcart.items.append(cart_item2)
        shopcart.update()

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)
        self.assertEqual(new_shopcart.items[1].product_name, cart_item2.product_name)

    def test_update_account_address(self):
        """It should Update a Shopcarts cart item"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        address = CartItemFactory(shopcart=shopcart)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        old_cart_item = shopcart.items[0]
        print("%r", old_cart_item)
        self.assertEqual(old_cart_item.quantity, address.quantity)
        # Change the product name
        old_cart_item.quantity = 36
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        address = shopcart.items[0]
        self.assertEqual(address.quantity, 36)

    def test_delete_shopcart_cart_item(self):
        """It should Delete an accounts address"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        cart_item = CartItemFactory(shopcart=shopcart)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        cart_item = shopcart.items[0]
        cart_item.delete()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)

    def test_find_shopcart_by_customer_id(self):
        """It should Find a shopcart by customer id"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Fetch it back by customer id
        same_shopcart = Shopcart.find_shopcart_by_customer_id(shopcart.customer_id)[0]
        self.assertEqual(same_shopcart.id, shopcart.id)
        self.assertEqual(same_shopcart.customer_id, shopcart.customer_id)

    def test_clear_items(self):
        """It should clear all CartItems in a Shopcart"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        [CartItemFactory(shopcart=shopcart) for _ in range(3)]
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart.clear_items()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)
