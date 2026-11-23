from playwright.sync_api import Page

from tests.locators import payments_locators as P


class PaymentsPage:
    def __init__(self, page: Page):
        self.page = page

    def create_payment(self, beneficiary: str, amount: str, currency: str = "GBP"):
        self.page.fill(P.BENEFICIARY, beneficiary)
        self.page.fill(P.AMOUNT, amount)
        self.page.select_option(P.CURRENCY, currency)
        self.page.click(P.SUBMIT)

    def message(self) -> str:
        return self.page.inner_text(P.MESSAGE)

    def error(self) -> str:
        return self.page.inner_text(P.ERROR)

    def table_text(self) -> str:
        return self.page.inner_text(P.TABLE)
