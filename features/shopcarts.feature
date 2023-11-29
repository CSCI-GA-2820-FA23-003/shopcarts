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