from pytest_bdd import given, parsers, scenarios, then, when

from tests.pages.login_page import LoginPage
from tests.pages.payments_page import PaymentsPage

scenarios("payments.feature")


@given("I am logged in", target_fixture="payments_page")
def logged_in(page, app_url, credentials):
    LoginPage(page, app_url).open().login(credentials["username"], credentials["password"])
    page.wait_for_url("**/payments*")
    return PaymentsPage(page)


@when(parsers.parse('I create a payment to "{beneficiary}" for "{amount}" "{currency}"'))
def create_payment(payments_page, beneficiary, amount, currency):
    payments_page.create_payment(beneficiary, amount, currency)


@then(parsers.parse('the payment status should be "{status}"'))
def payment_status(payments_page, status):
    assert status in payments_page.message()


@then(parsers.parse('the payments table should contain "{text}"'))
def table_contains(payments_page, text):
    assert text in payments_page.table_text()


@then(parsers.parse('I should see the payment error "{text}"'))
def payment_error(payments_page, text):
    assert text in payments_page.error()
