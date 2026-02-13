import { test, expect } from "@playwright/test";

/**
 * Comprehensive frontend inspection test suite.
 * Captures console errors, network failures, and accessibility issues.
 */

test.describe("Frontend Inspection", () => {
  test("home page loads without console errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    const consoleWarnings: string[] = [];

    // Capture console messages
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
      if (msg.type() === "warning") {
        consoleWarnings.push(msg.text());
      }
    });

    // Capture page errors
    page.on("pageerror", (error) => {
      consoleErrors.push(error.message);
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Log findings
    if (consoleErrors.length > 0) {
      console.log("Console Errors:", consoleErrors);
    }
    if (consoleWarnings.length > 0) {
      console.log("Console Warnings:", consoleWarnings);
    }

    // Take screenshot for visual inspection
    await page.screenshot({ path: "e2e/screenshots/home.png", fullPage: true });

    // Check for critical errors (filter out expected auth redirects)
    const criticalErrors = consoleErrors.filter(
      (e) => !e.includes("clerk") && !e.includes("auth") && !e.includes("sign-in")
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test("dashboard page inspection", async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    page.on("pageerror", (error) => {
      consoleErrors.push(error.message);
    });

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await page.screenshot({ path: "e2e/screenshots/dashboard.png", fullPage: true });

    console.log("Dashboard console errors:", consoleErrors);
  });

  test("coaching page inspection", async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    page.on("pageerror", (error) => {
      consoleErrors.push(error.message);
    });

    await page.goto("/coaching");
    await page.waitForLoadState("networkidle");

    await page.screenshot({ path: "e2e/screenshots/coaching.png", fullPage: true });

    console.log("Coaching console errors:", consoleErrors);
  });

  test("calls page inspection", async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    page.on("pageerror", (error) => {
      consoleErrors.push(error.message);
    });

    await page.goto("/calls");
    await page.waitForLoadState("networkidle");

    await page.screenshot({ path: "e2e/screenshots/calls.png", fullPage: true });

    console.log("Calls console errors:", consoleErrors);
  });

  test("check network requests for failures", async ({ page }) => {
    const failedRequests: string[] = [];

    page.on("requestfailed", (request) => {
      failedRequests.push(`${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });

    page.on("response", (response) => {
      if (response.status() >= 400 && response.status() !== 401) {
        failedRequests.push(`${response.status()} ${response.url()}`);
      }
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    if (failedRequests.length > 0) {
      console.log("Failed network requests:", failedRequests);
    }
  });

  test("accessibility check - color contrast and labels", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check for images without alt text
    const imagesWithoutAlt = await page.locator("img:not([alt])").count();
    console.log(`Images without alt text: ${imagesWithoutAlt}`);

    // Check for buttons without accessible names
    const buttonsWithoutLabel = await page
      .locator("button:not([aria-label]):not(:has-text(.))")
      .count();
    console.log(`Buttons without accessible names: ${buttonsWithoutLabel}`);

    // Check for inputs without labels
    const inputsWithoutLabel = await page.locator("input:not([aria-label]):not([id])").count();
    console.log(`Inputs without accessible labels: ${inputsWithoutLabel}`);

    // Check for links without href
    const linksWithoutHref = await page.locator("a:not([href])").count();
    console.log(`Links without href: ${linksWithoutHref}`);
  });

  test("responsive design check - mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.screenshot({ path: "e2e/screenshots/home-mobile.png", fullPage: true });

    // Check for horizontal overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });

    if (hasHorizontalScroll) {
      console.log("Warning: Page has horizontal scroll on mobile");
    }
  });

  test("check for hydration errors", async ({ page }) => {
    const hydrationErrors: string[] = [];

    page.on("console", (msg) => {
      const text = msg.text();
      if (
        text.includes("Hydration") ||
        text.includes("hydration") ||
        text.includes("server-rendered") ||
        text.includes("did not match")
      ) {
        hydrationErrors.push(text);
      }
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    if (hydrationErrors.length > 0) {
      console.log("Hydration errors detected:", hydrationErrors);
    }

    expect(hydrationErrors).toHaveLength(0);
  });
});
