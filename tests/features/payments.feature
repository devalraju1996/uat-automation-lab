Feature: Create payments
  Background:
    Given I am logged in

  @smoke
  Scenario: Create a valid GBP payment
    When I create a payment to "Acme Ltd" for "250.00" "GBP"
    Then the payment status should be "ACCEPTED"
    And the payments table should contain "Acme Ltd"

  @regression
  Scenario: Payment to a sanctioned beneficiary is rejected
    When I create a payment to "Blocked Corp" for "100" "USD"
    Then the payment status should be "REJECTED_SANCTIONS"

  @regression
  Scenario Outline: Invalid payments are rejected
    When I create a payment to "Acme Ltd" for "<amount>" "<currency>"
    Then I should see the payment error "<error>"

    Examples:
      | amount | currency | error                          |
      | 0      | GBP      | Amount must be greater than zero |
      | 10     | JPY      | Unsupported currency JPY       |
