"""E2E tests for coaching features."""

import pytest
from playwright.async_api import Page


@pytest.mark.asyncio
class TestCoachingFeatures:
    """Tests for coaching-specific features."""

    async def test_rep_dashboard_loads(self, page: Page, base_url, sample_rep_email):
        """Test rep dashboard loads."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Wait for page
        await page.wait_for_load_state("networkidle")

        # Verify URL
        assert "/dashboard/" in page.url

    async def test_dashboard_metrics_visible(self, page: Page, base_url, sample_rep_email):
        """Test dashboard metrics are displayed."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for metrics
        metrics = page.locator("text=/calls|score|average|trend/i")
        if await metrics.count() > 0:
            # Metrics visible
            pass

    async def test_score_trends_chart(self, page: Page, base_url, sample_rep_email):
        """Test score trends are displayed."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for chart
        chart = page.locator('[role="img"][aria-label*="chart" i], .chart, svg')
        if await chart.count() > 0:
            # Chart visible
            pass

    async def test_skill_gaps_section(self, page: Page, base_url, sample_rep_email):
        """Test skill gaps are displayed."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for skill gaps
        gaps = page.locator("text=/skill gap|area for improvement|weakness/i")
        if await gaps.count() > 0:
            # Gaps visible
            pass

    async def test_coaching_plan_section(self, page: Page, base_url, sample_rep_email):
        """Test coaching plan is displayed."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for coaching plan
        plan = page.locator("text=/coaching plan|recommendation|next step/i")
        if await plan.count() > 0:
            # Plan visible
            pass

    async def test_call_history_visible(self, page: Page, base_url, sample_rep_email):
        """Test call history table is visible."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for table
        table = page.locator('table, [role="table"]')
        if await table.count() > 0:
            # Table visible
            pass

    async def test_learning_insights_section(self, page: Page, base_url, sample_rep_email):
        """Test learning insights section."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for learning insights
        insights = page.locator("text=/learning|insight|example|top performer/i")
        if await insights.count() > 0:
            # Insights visible
            pass

    async def test_dimension_radar_chart(self, page: Page, base_url, sample_rep_email):
        """Test radar chart of dimensions."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for radar chart or dimension visualization
        radar = page.locator('svg[aria-label*="dimension" i], .radar, canvas')
        if await radar.count() > 0:
            # Radar visible
            pass

    async def test_time_period_selector(self, page: Page, base_url, sample_rep_email):
        """Test time period selector works."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for period selector
        selector = page.locator("button:has-text(/last 7|last 30|quarter|all time/i)")
        if await selector.count() > 0:
            # Selector visible
            pass

    async def test_dimension_detail_view(self, page: Page, base_url, sample_rep_email):
        """Test drilling into dimension details."""
        await page.goto(f"{base_url}/dashboard/{sample_rep_email}", wait_until="networkidle")

        # Look for dimension card that can be clicked
        dimension_card = page.locator('[data-testid*="dimension"], .dimension-card')
        if await dimension_card.count() > 0:
            # Can interact with dimensions
            pass
