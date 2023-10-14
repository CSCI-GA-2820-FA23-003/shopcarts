"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import ShopcartFactory, CartItemFactory
from service import app
from service.models import db
from service.common import status  # HTTP Status Codes

BASE_URL = "/shopcarts"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    def test_create_account(self):
        """It should Create a empty shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL + "/" + str(shopcart.customer_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["customer_id"], shopcart.customer_id, "customer_id does not match")
        self.assertEqual(new_shopcart["items"], [], "Items does not match")