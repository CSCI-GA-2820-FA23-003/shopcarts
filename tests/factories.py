# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyFloat, FuzzyInteger
from service.models import Shopcart, CartItem


class ShopcartFactory(factory.Factory):
    """Creates fake Shopcarts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class CartItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = CartItem

    id = factory.Sequence(lambda n: n)
    shopcart_id = None
    product_name = FuzzyChoice(
        choices=["iPhone", "iPad", "MacBook", "Google Pixel", "Apple Watch"]
    )
    quantity = FuzzyInteger(1, 10)
    price = FuzzyFloat(0.1, 51.0)
    shopcart = factory.SubFactory(ShopcartFactory)
