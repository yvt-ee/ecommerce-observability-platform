"""
Shared pytest fixtures.

Points the app at an isolated SQLite file and disables OpenTelemetry
before `app.main` is ever imported, so tests are fast, hermetic, and don't
try to reach a collector that isn't running.
"""
import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "test_ecommerce.db"

os.environ["OTEL_ENABLED"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db():
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def client():
    # Using `with` triggers FastAPI's lifespan (creates tables + seeds
    # products), matching what happens when the app really starts.
    with TestClient(app) as c:
        yield c
