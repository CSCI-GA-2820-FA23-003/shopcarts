import os
import requests
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following shopcarts')
def step_impl(context):
    """Delete all shopcarts and load new ones"""

    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK

    # List all shopcarts and delete them one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # Load the database with new shopcarts
    for row in context.table:
        payload = {
            "customer_id": row['customer_id']
        }

        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED

@given('the following cartitems')
def step_impl(context):
    """Delete all cart items and load new ones"""

    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK

    shopcarts = {}
    for shopcart in context.resp.json():
        shopcarts[shopcart["customer_id"]] = shopcart["id"]

    # Load the database with new shopcarts
    for row in context.table:
        customer_id = row['customer_id']
        shopcart_id = shopcarts.get(int(customer_id), None)
        payload = {
            "price": row['price'],
            "product_id": row['product_id'],
            "quantity": row['quantity'],
            "shopcart_id": shopcart_id
        }

        rest_endpoint = f"{context.base_url}/shopcarts/{shopcart_id}/items"
        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED

@when('I visit the "Home Page"')
def step_impl(context):
    """Visit the base url"""
    context.driver.get(context.base_url + '/')
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@given('the server is running')
def step_impl(context):
    """Verify the server is running"""
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """The home page title should be visible on the page"""
    print(context.driver.title)
    assert message in str(context.driver.title)

@then('I should not see "{message}"')
def step_impl(context, message):
    """There should be no errors on the page"""
    assert message not in str(context.resp.text)

@when('I press the "{button}" button')
def step_impl(context, button):
    """Presses button on the UI"""
    button_id = button.lower() + '-btn'
    context.driver.find_element(By.ID, button_id).click()

@then('I should see "{element_id}" in the results')
def step_impl(context, element_id):
    """Verifies visibility of <td> with id=element_id in the results table"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located(
            (By.ID, element_id)
        )
    )
    assert found

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    """Verifies absence of <td> with id=element_id in the results table"""
    found_element = False
    context.driver.implicitly_wait(1)
    try:
        context.driver.find_element(By.ID, name)
        found_element = True
    except NoSuchElementException:
        pass

    context.driver.implicitly_wait(context.wait_seconds)
    assert found_element is False

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert found
