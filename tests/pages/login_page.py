from playwright.sync_api import Page

from tests.locators import login_locators as L


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page, self.base_url = page, base_url

    def open(self):
        self.page.goto(self.base_url + "/")
        return self

    def login(self, username: str, password: str):
        self.page.fill(L.USERNAME, username)
        self.page.fill(L.PASSWORD, password)
        self.page.click(L.LOGIN_BUTTON)

    def error_text(self) -> str:
        return self.page.inner_text(L.LOGIN_ERROR)
