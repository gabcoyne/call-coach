"""Pytest configuration for E2E tests."""

import os

import pytest
from playwright.async_api import Browser, BrowserContext, async_playwright


@pytest.fixture(scope="session")
def base_url():
    """Get base URL for testing."""
    return os.getenv("BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
async def browser():
    """Create browser instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=os.getenv("HEADLESS", "true").lower() == "true")
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser):
    """Create browser context."""
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext):
    """Create page instance."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def test_user():
    """Test user credentials."""
    return {
        "email": os.getenv("TEST_USER_EMAIL", "test@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "test-password"),
    }


@pytest.fixture
def sample_call_id():
    """Sample call ID for testing."""
    return os.getenv("TEST_CALL_ID", "1234567890")


@pytest.fixture
def sample_rep_email():
    """Sample rep email for testing."""
    return os.getenv("TEST_REP_EMAIL", "sarah@example.com")
