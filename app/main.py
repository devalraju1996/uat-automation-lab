"""Demo 'Payments Portal' - the application under test (AUT) for UAT automation.

Simulates a small banking UI: login, create a payment, view payment list,
plus a REST API and a health endpoint used by Kubernetes/ECS probes.
"""

import os
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

APP_ENV = os.getenv("APP_ENV", "local")
DEMO_USER = os.getenv("DEMO_USER", "uat_user")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Passw0rd!")
SUPPORTED_CURRENCIES = {"GBP", "USD", "EUR"}
SANCTIONED_NAMES = {"blocked corp"}  # stand-in for OFAC screening

app = FastAPI(title="Payments Portal (UAT demo)")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
PAYMENTS: list[dict] = []
SESSIONS: set[str] = set()


class PaymentIn(BaseModel):
    beneficiary: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = "GBP"


def _create_payment(beneficiary: str, amount: float, currency: str) -> dict:
    currency = currency.upper()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency {currency}")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    status = "REJECTED_SANCTIONS" if beneficiary.strip().lower() in SANCTIONED_NAMES else "ACCEPTED"
    payment = {
        "id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
        "beneficiary": beneficiary.strip(),
        "amount": round(amount, 2),
        "currency": currency,
        "status": status,
        "created_at": datetime.now(UTC).isoformat(),
    }
    PAYMENTS.append(payment)
    return payment


def _logged_in(request: Request) -> bool:
    return request.cookies.get("session") in SESSIONS


@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse(request, "login.html", {"error": error, "env": APP_ENV})


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == DEMO_USER and password == DEMO_PASSWORD:
        token = uuid.uuid4().hex
        SESSIONS.add(token)
        resp = RedirectResponse("/payments", status_code=303)
        resp.set_cookie("session", token, httponly=True)
        return resp
    return RedirectResponse("/?error=Invalid+username+or+password", status_code=303)


@app.get("/logout")
def logout(request: Request):
    SESSIONS.discard(request.cookies.get("session"))
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("session")
    return resp


@app.get("/payments", response_class=HTMLResponse)
def payments_page(request: Request, message: str | None = None, error: str | None = None):
    if not _logged_in(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request,
        "payments.html",
        {"payments": list(reversed(PAYMENTS)), "message": message, "error": error, "env": APP_ENV},
    )


@app.post("/payments")
def submit_payment(
    request: Request, beneficiary: str = Form(...), amount: str = Form(...), currency: str = Form("GBP")
):
    if not _logged_in(request):
        return RedirectResponse("/", status_code=303)
    try:
        p = _create_payment(beneficiary, float(amount), currency)
    except ValueError as exc:
        return RedirectResponse(f"/payments?error={exc}", status_code=303)
    return RedirectResponse(f"/payments?message=Payment+{p['id']}+{p['status']}", status_code=303)


@app.get("/api/payments")
def list_payments():
    return PAYMENTS


@app.post("/api/payments", status_code=201)
def api_create_payment(body: PaymentIn):
    try:
        return _create_payment(body.beneficiary, body.amount, body.currency)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.delete("/api/payments", status_code=204)
def reset_payments():
    """Test-data reset hook (only meant for non-prod envs)."""
    if APP_ENV == "prod":
        raise HTTPException(status_code=403, detail="Not allowed in prod")
    PAYMENTS.clear()
