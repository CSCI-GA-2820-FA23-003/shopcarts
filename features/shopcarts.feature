Feature: The shopcart service back-end
    As a e-commerce shop business manager
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts

Background:
    Given the following shopcarts
        | customer_id |
        | 1           |
        | 2           |
        | 3           |
    And the following cartitems
        | product_id  | price     | quantity | customer_id |
        | 1           | 1.0       | 2        | 1           |
        | 1           | 1.0       | 1        | 2           |
        | 2           | 3.0       | 3        | 1           |
        | 3           | 2.5       | 1        | 1           |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    And I should see "customer-id-2" in the results
    And I should not see "customer-id-4" in the results

Scenario: Create a shopcart
    When I visit the "Home Page"
    And I set the "customer_id" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "4" in the "customer_id" field

Scenario: Delete a shopcart
    When I visit the "Home Page"
    And I set the "customer_id" to "3"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-3" in the results
    When I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should not see "customer-id-3" in the results

Scenario: Add product to a shopcart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "CartItem Shopcart ID" field
    And I set the "product_id" to "4"
    And I set the "price" to "5"
    And I set the "quantity" to "2"
    And I press the "CartItem-Create" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-4" in the results

Scenario: Delete an Item from a Shopcart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "CartItem Shopcart ID" field
    And I set the "product_id" to "4"
    And I set the "price" to "5"
    And I set the "quantity" to "2"
    And I press the "CartItem-Create" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-4" in the results
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "CartItem Shopcart ID" field
    And I set the "product_id" to "4"
    And I press the "CartItem-Delete" button
    Then I should see the message "Success"
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I set the "Customer ID" to "4"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "product-id-4" in the results

Scenario: Query Shopcart by customer id
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    And I should see "customer-id-2" in the results
    And I should see "customer-id-3" in the results
    And I should not see "customer-id-4" in the results
    When I set the "customer_id" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I set the "customer_id" to "4"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-4" in the results
    And I should not see "customer-id-3" in the results
    And I should not see "customer-id-2" in the results
    And I should not see "customer-id-1" in the results
    When I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty

Scenario: Read Shopcart by shopcart id (Retrieve)
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    And I should see "customer-id-2" in the results
    And I should see "customer-id-3" in the results
    And I should not see "customer-id-4" in the results
    When I set the "customer_id" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "4" in the "customer_id" field
    And I should see "customer-id-4" in the results
    And I should not see "customer-id-3" in the results
    And I should not see "customer-id-2" in the results
    And I should not see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Delete" button
    Then I should see the message "Deleted!"
    When I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Read Shopcart by shopcart id (Search)
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    And I should see "customer-id-2" in the results
    And I should see "customer-id-3" in the results
    And I should not see "customer-id-4" in the results
    When I set the "customer_id" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "4" in the "customer_id" field
    And I should see "customer-id-4" in the results
    And I should not see "customer-id-3" in the results
    And I should not see "customer-id-2" in the results
    And I should not see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Delete" button
    Then I should see the message "Deleted!"
    When I press the "Clear" button
    Then the "customer_id" field should be empty
    And the "shopcart_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Search" button
    Then I should see the message "404 Not Found"

Scenario: Clear shopcart items by shopcart id
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    And I should see "customer-id-2" in the results
    And I should see "customer-id-3" in the results
    And I should not see "customer-id-4" in the results
    When I copy the "shopcart_id" field
    And I press the "ClearCart" button
    Then I should see the message "Shopcart has been cleared!"
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should not see "product-id-1" in the results
    And I should not see "product-id-2" in the results
    And I should not see "product-id-3" in the results
    And I should not see "product-id-4" in the results

Scenario: Update the quantity of a product in a shop cart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id" field
    And I set the "product_id" to "1"
    And I set the "quantity" to "99"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "quantity" being "99"
    When I set the "quantity" to "999"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "quantity" being "999"
    And I should not see "product-id-1" in the results with "quantity" being "99"

Scenario: Update the price of a product in a shop cart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id" field
    And I set the "product_id" to "1"
    And I set the "price" to "99"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "price" being "99"
    When I set the "price" to "999"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "price" being "999"

Scenario: Update the quantity and price of a product in a shopcart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "customer-id-1" in the results
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id" field
    And I set the "product_id" to "1"
    And I set the "quantity" to "99"
    And I set the "price" to "66"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "quantity" being "99"
    And I should see "product-id-1" in the results with "price" being "66"
    When I set the "quantity" to "999"
    And I set the "price" to "666"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "product-id-1" in the results with "quantity" being "999"
    And I should see "product-id-1" in the results with "price" being "666"