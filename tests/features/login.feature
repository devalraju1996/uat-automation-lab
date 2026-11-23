@smoke
Feature: Login to the Payments Portal
  As a UAT tester I want to log in so I can test payment journeys

  Scenario: Successful login
    Given I am on the login page
    When I log in with valid credentials
    Then I should see the payments page

  Scenario: Login with wrong password
    Given I am on the login page
    When I log in as "uat_user" with password "wrong"
    Then I should see the login error "Invalid username or password"
