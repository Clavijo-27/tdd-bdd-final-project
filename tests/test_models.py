# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        new_description = "Updated description"
        product.description = new_description
        product.update()
        found = Product.find(product.id)
        self.assertEqual(found.description, new_description)
        self.assertEqual(found.id, product.id)
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)
        self.assertEqual(all_products[0].description, new_description)

    def test_delete_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products"""
        self.assertEqual(len(Product.all()), 0)
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """It should find products by name"""
        products = [ProductFactory() for _ in range(5)]
        for product in products:
            product.id = None
            product.create()
        name = products[0].name
        expected_count = sum(1 for p in products if p.name == name)
        found = Product.find_by_name(name).all()
        self.assertEqual(len(found), expected_count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should find products by availability"""
        products = [ProductFactory() for _ in range(10)]
        for product in products:
            product.id = None
            product.create()
        available = products[0].available
        expected_count = sum(1 for p in products if p.available == available)
        found = Product.find_by_availability(available).all()
        self.assertEqual(len(found), expected_count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should find products by category"""
        products = [ProductFactory() for _ in range(10)]
        for product in products:
            product.id = None
            product.create()
        category = products[0].category
        expected_count = sum(1 for p in products if p.category == category)
        found = Product.find_by_category(category).all()
        self.assertEqual(len(found), expected_count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_deserialize_invalid_boolean(self):
        """It should raise DataValidationError for invalid boolean type in deserialize"""
        product = Product()
        data = {
            "name": "Test",
            "description": "desc",
            "price": "10.0",
            "available": "not_a_bool",
            "category": "CLOTHS"
        }
        with self.assertRaises(Exception) as context:
            product.deserialize(data)
        self.assertIn("Invalid type for boolean", str(context.exception))

    def test_deserialize_invalid_attribute(self):
        """It should raise DataValidationError for invalid category attribute in deserialize"""
        product = Product()
        data = {
            "name": "Test",
            "description": "desc",
            "price": "10.0",
            "available": True,
            "category": "NOT_A_CATEGORY"
        }
        with self.assertRaises(Exception) as context:
            product.deserialize(data)
        self.assertIn("Invalid attribute", str(context.exception))

    def test_deserialize_missing_key(self):
        """It should raise DataValidationError for missing key in deserialize"""
        product = Product()
        data = {
            "description": "desc",
            "price": "10.0",
            "available": True,
            "category": "CLOTHS"
        }
        with self.assertRaises(Exception) as context:
            product.deserialize(data)
        self.assertIn("missing name", str(context.exception))

    def test_deserialize_type_error(self):
        """It should raise DataValidationError for type error in deserialize"""
        product = Product()
        with self.assertRaises(Exception) as context:
            product.deserialize(None)
        self.assertIn("body of request contained bad or no data", str(context.exception))

    def test_find_by_category_unknown(self):
        """It should return products with category UNKNOWN (even if none)"""
        # Ensure at least one product with UNKNOWN
        product = ProductFactory(category=Category.UNKNOWN)
        product.id = None
        product.create()
        found = Product.find_by_category(Category.UNKNOWN).all()
        self.assertTrue(any(p.category == Category.UNKNOWN for p in found))
