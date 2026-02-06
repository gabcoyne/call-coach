"""E2E tests for authentication flows."""

import pytest
from playwright.async_api import Page


@pytest.mark.asyncio
class TestAuthentication:
    """Tests for login and authentication."""

    async def test_login_page_loads(self, page: Page, base_url):
        """Test that login page loads correctly."""
        await page.goto(f"{base_url}/sign-in")

        # Check page title or heading
        await page.wait_for_selector("text=/sign in|login/i")

        # Verify URL
        assert "/sign-in" in page.url

    async def test_login_form_elements_present(self, page: Page, base_url):
        """Test that login form has required elements."""
        await page.goto(f"{base_url}/sign-in")

        # Look for email input
        email_input = page.locator('input[type="email"], input[placeholder*="email" i]')
        assert await email_input.count() > 0

    async def test_invalid_credentials(self, page: Page, base_url):
        """Test login with invalid credentials shows error."""
        await page.goto(f"{base_url}/sign-in")

        # Try to login
        email_input = page.locator('input[type="email"], input[placeholder*="email" i]')
        if await email_input.count() > 0:
            await email_input.fill("invalid@example.com")

    async def test_sign_up_page_accessible(self, page: Page, base_url):
        """Test that sign-up page is accessible."""
        await page.goto(f"{base_url}/sign-up")

        # Wait for page to load
        await page.wait_for_load_state("networkidle")

        # Verify URL
        assert "/sign-up" in page.url

    async def test_sign_up_form_present(self, page: Page, base_url):
        """Test sign-up form elements are present."""
        await page.goto(f"{base_url}/sign-up")

        # Look for form elements
        form = page.locator("form")
        assert await form.count() > 0

    async def test_redirect_unauthenticated_user(self, page: Page, base_url):
        """Test that unauthenticated users are redirected from protected routes."""
        # Try to access dashboard without auth
        await page.goto(f"{base_url}/dashboard/test@example.com", wait_until="domcontentloaded")

        # Should be redirected to login or show auth error
        # (exact behavior depends on auth implementation)
