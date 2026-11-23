"""Shared fixtures: start the app locally (or point at a deployed UAT env),
browser config, test-data reset and screenshot-on-failure."""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def app_url():
    """Use UAT_BASE_URL if set (deployed env), otherwise boot the app locally."""
    url = os.getenv("UAT_BASE_URL")
    if url:
        yield url.rstrip("/")
        return
    port = os.getenv("LOCAL_PORT", "8000")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", port],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            if requests.get(f"{url}/health", timeout=1).ok:
                break
        except requests.ConnectionError:
            time.sleep(0.2)
    yield url
    proc.terminate()


@pytest.fixture(autouse=True)
def reset_test_data(app_url):
    requests.delete(f"{app_url}/api/payments", timeout=5)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Allow a pre-installed browser (e.g. corporate Edge/Chrome) via env var."""
    path = os.getenv("BROWSER_EXECUTABLE_PATH")
    return {**browser_type_launch_args, **({"executable_path": path} if path else {})}


@pytest.fixture
def credentials():
    return {
        "username": os.getenv("DEMO_USER", "uat_user"),
        "password": os.getenv("DEMO_PASSWORD", "Passw0rd!"),
    }
