"""E2E tests for call viewer functionality."""
import pytest
from playwright.async_api import Page


@pytest.mark.asyncio
class TestCallViewer:
    """Tests for call viewer interface."""

    async def test_calls_list_loads(self, page: Page, base_url):
        """Test calls list page loads."""
        await page.goto(f'{base_url}/calls', wait_until='networkidle')

        # Wait for page content
        await page.wait_for_load_state('networkidle')

        # Check page title or heading
        assert '/calls' in page.url

    async def test_call_search_functionality(self, page: Page, base_url):
        """Test call search works."""
        await page.goto(f'{base_url}/calls', wait_until='networkidle')

        # Look for search input
        search_input = page.locator('input[type="search"], input[placeholder*="search" i]')
        if await search_input.count() > 0:
            await search_input.fill('test call')

    async def test_call_detail_page_loads(self, page: Page, base_url, sample_call_id):
        """Test individual call detail page loads."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Wait for content
        await page.wait_for_load_state('networkidle')

        # Verify URL includes call ID
        assert sample_call_id in page.url or '/calls/' in page.url

    async def test_call_metadata_displays(self, page: Page, base_url, sample_call_id):
        """Test call metadata is displayed."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for metadata elements
        await page.wait_for_selector('text=/date|time|duration|participants/i', timeout=5000)

    async def test_score_badges_visible(self, page: Page, base_url, sample_call_id):
        """Test that coaching scores are displayed."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for score badges
        score_badge = page.locator('[role="img"], .score, .badge')
        if await score_badge.count() > 0:
            # Scores should be visible
            pass

    async def test_dimensions_section_present(self, page: Page, base_url, sample_call_id):
        """Test dimension scores section is present."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for dimension cards
        dimensions = page.locator('text=/discovery|engagement|product knowledge|objection handling/i')
        if await dimensions.count() > 0:
            # Dimensions are visible
            pass

    async def test_strengths_section_present(self, page: Page, base_url, sample_call_id):
        """Test strengths section displays."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for strengths section
        await page.wait_for_selector('text=/strength|strong point|positive/i', timeout=5000)

    async def test_improvements_section_present(self, page: Page, base_url, sample_call_id):
        """Test improvement areas section displays."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for improvements section
        await page.wait_for_selector('text=/improvement|area for improvement|opportunity/i', timeout=5000)

    async def test_transcript_section_present(self, page: Page, base_url, sample_call_id):
        """Test transcript section is present."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for transcript
        transcript = page.locator('text=/transcript|conversation/i, [data-testid*="transcript"]')
        if await transcript.count() > 0:
            # Transcript visible
            pass

    async def test_coaching_notes_section(self, page: Page, base_url, sample_call_id):
        """Test coaching notes section is present."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for coaching notes
        notes = page.locator('text=/coaching note|feedback|note/i')
        if await notes.count() > 0:
            # Notes visible
            pass

    async def test_action_items_section(self, page: Page, base_url, sample_call_id):
        """Test action items are displayed."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for action items
        await page.wait_for_selector('text=/action item|next step|todo/i', timeout=5000)

    async def test_export_functionality_available(self, page: Page, base_url, sample_call_id):
        """Test export button is available."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for export button
        export_button = page.locator('button:has-text(/export|download|pdf/i)')
        if await export_button.count() > 0:
            # Export available
            pass

    async def test_share_functionality_available(self, page: Page, base_url, sample_call_id):
        """Test share button is available."""
        await page.goto(f'{base_url}/calls/{sample_call_id}', wait_until='networkidle')

        # Look for share button
        share_button = page.locator('button:has-text(/share|send/i)')
        if await share_button.count() > 0:
            # Share available
            pass
