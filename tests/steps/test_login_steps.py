import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from tests.pages.login_page import LoginPage

scenarios("login.feature")


@given("I am on the login page", target_fixture="login_page")
def on_login_page(page, app_url):
    return LoginPage(page, app_url).open()


@when("I log in with valid credentials")
def login_valid(login_page, credentials):
    login_page.login(credentials["username"], credentials["password"])


@when(parsers.parse('I log in as "{user}" with password "{password}"'))
def login_as(login_page, user, password):
    login_page.login(user, password)


@then("I should see the payments page")
def see_payments(page):
    expect(page).to_have_url(re.compile(r".*/payments(\?.*)?$"))


@then(parsers.parse('I should see the login error "{text}"'))
def see_login_error(login_page, text):
    assert text in login_page.error_text()


@when("I log out")
def log_out(page):
    page.click('[data-testid="logout"]')


@then("I should be on the login page")
def on_login(page):
    expect(page.locator('[data-testid="login-button"]')).to_be_visible()
