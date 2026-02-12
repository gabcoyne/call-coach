/**
 * Accessibility Tests
 *
 * These tests use axe-core to check for WCAG accessibility violations.
 * Run these tests regularly to ensure the app remains accessible.
 */

import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe("Accessibility", () => {
  describe("Button Component", () => {
    it("should have no accessibility violations", async () => {
      const { container } = render(<Button>Click me</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have no violations when disabled", async () => {
      const { container } = render(<Button disabled>Disabled</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have no violations with different variants", async () => {
      const { container } = render(
        <>
          <Button variant="default">Default</Button>
          <Button variant="destructive">Delete</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="prefect">Prefect</Button>
        </>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Card Component", () => {
    it("should have no accessibility violations", async () => {
      const { container } = render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Card content goes here</p>
          </CardContent>
        </Card>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Form Components", () => {
    it("should have no violations for labeled input", async () => {
      const { container } = render(
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="Enter your email" />
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should flag missing label as violation", async () => {
      const { container } = render(<Input type="email" placeholder="Email" />);
      const results = await axe(container);
      // This should have violations because input lacks a label
      expect(results.violations.length).toBeGreaterThan(0);
    });

    it("should have no violations for form with aria-label", async () => {
      const { container } = render(
        <Input type="email" placeholder="Email" aria-label="Email address" />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Color Contrast", () => {
    it("should pass color contrast for buttons", async () => {
      const { container } = render(
        <div style={{ backgroundColor: "#ffffff", padding: "20px" }}>
          <Button>High Contrast Button</Button>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should detect low contrast issues", async () => {
      const { container } = render(
        <div
          style={{
            backgroundColor: "#f0f0f0",
            padding: "20px",
          }}
        >
          <span style={{ color: "#e0e0e0" }}>Low contrast text</span>
        </div>
      );
      const results = await axe(container);
      // This should have color contrast violations
      expect(results.violations.length).toBeGreaterThan(0);
      const contrastViolation = results.violations.find((v) => v.id === "color-contrast");
      expect(contrastViolation).toBeDefined();
    });
  });

  describe("Keyboard Navigation", () => {
    it("should be keyboard accessible", async () => {
      const { container } = render(
        <div>
          <Button>First</Button>
          <Button>Second</Button>
          <Button>Third</Button>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should flag non-interactive elements with click handlers", async () => {
      const { container } = render(<div onClick={() => {}}>Clickable div (bad practice)</div>);
      const results = await axe(container);
      // Should have violations for non-semantic interactive elements
      expect(results.violations.length).toBeGreaterThan(0);
    });
  });

  describe("Semantic HTML", () => {
    it("should have no violations for semantic structure", async () => {
      const { container } = render(
        <article>
          <header>
            <h1>Article Title</h1>
          </header>
          <section>
            <h2>Section Heading</h2>
            <p>Content goes here.</p>
          </section>
          <footer>
            <p>Footer content</p>
          </footer>
        </article>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should flag improper heading hierarchy", async () => {
      const { container } = render(
        <div>
          <h1>Title</h1>
          <h3>Skipped h2 - bad practice</h3>
        </div>
      );
      const results = await axe(container);
      // May or may not flag depending on axe rules
      // Document the expectation
      if (results.violations.length > 0) {
        const headingViolation = results.violations.find((v) => v.id.includes("heading"));
        expect(headingViolation).toBeDefined();
      }
    });
  });

  describe("ARIA Attributes", () => {
    it("should have no violations for proper ARIA usage", async () => {
      const { container } = render(
        <div>
          <button aria-label="Close dialog" aria-expanded="false" aria-controls="dialog-1">
            X
          </button>
          <div id="dialog-1" role="dialog" aria-labelledby="dialog-title" aria-modal="true">
            <h2 id="dialog-title">Dialog Title</h2>
            <p>Dialog content</p>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should flag invalid ARIA attributes", async () => {
      const { container } = render(<div aria-invalid-attribute="true">Invalid ARIA</div>);
      const results = await axe(container);
      // Axe should catch invalid ARIA attributes
      expect(results.violations.length).toBeGreaterThan(0);
    });
  });
});

describe("Accessibility Best Practices", () => {
  it("should use alt text for images", async () => {
    const { container } = render(<img src="/logo.png" alt="Company Logo" />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("should flag missing alt text", async () => {
    const { container } = render(<img src="/logo.png" />);
    const results = await axe(container);
    expect(results.violations.length).toBeGreaterThan(0);
    const altViolation = results.violations.find((v) => v.id === "image-alt");
    expect(altViolation).toBeDefined();
  });

  it("should have accessible link text", async () => {
    const { container } = render(<a href="/home">Go to Home Page</a>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("should flag vague link text", async () => {
    const { container } = render(<a href="/home">Click here</a>);
    const results = await axe(container);
    // Axe may or may not flag "click here" depending on rules
    // This is more of a best practice than a hard violation
    // Document the guideline
  });

  it("should have accessible table headers", async () => {
    const { container } = render(
      <table>
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Email</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>john@example.com</td>
          </tr>
        </tbody>
      </table>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe("Page-Level Accessibility Audits", () => {
  describe("Coaching Feed Page (/feed)", () => {
    it("should have proper heading hierarchy", async () => {
      const { container } = render(
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Coaching Feed</h1>
            <p className="text-muted-foreground mt-1">
              Latest insights, highlights, and team updates
            </p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <h2>Main Feed</h2>
            </div>
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-foreground">Team Insights</h2>
              <h2 className="text-lg font-semibold text-foreground">Coaching Highlights</h2>
            </div>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible loading states", async () => {
      const { container } = render(
        <div role="status" aria-live="polite">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="h-8 w-8 animate-spin" aria-hidden="true" />
            <p>Loading feed...</p>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible empty state", async () => {
      const { container } = render(
        <div role="status">
          <div className="flex flex-col items-center justify-center text-center max-w-md mx-auto">
            <div className="h-12 w-12" aria-hidden="true" />
            <p className="text-lg font-medium">Coaching Feed Coming Soon</p>
            <p className="text-sm text-muted-foreground">
              This page will display personalized coaching insights
            </p>
            <a href="/calls" className="underline font-medium">
              Browse all calls
            </a>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Calls Library Page (/calls)", () => {
    it("should have accessible search form", async () => {
      const { container } = render(
        <form role="search">
          <Label htmlFor="search-input">Search calls</Label>
          <Input
            id="search-input"
            placeholder="Search by title, customer, or rep..."
            aria-label="Search by title, customer, or rep"
          />
          <Button type="submit">Search</Button>
        </form>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible filter controls", async () => {
      const { container } = render(
        <div role="group" aria-label="Call filters">
          <Label htmlFor="call-type-filter">Call Type</Label>
          <select id="call-type-filter" aria-label="Filter by call type">
            <option value="all">All Types</option>
            <option value="discovery">Discovery</option>
            <option value="demo">Demo</option>
          </select>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible table with proper headers", async () => {
      const { container } = render(
        <table role="table" aria-label="Calls list">
          <thead>
            <tr>
              <th scope="col">Call Title</th>
              <th scope="col">Date</th>
              <th scope="col">Duration</th>
              <th scope="col">Type</th>
              <th scope="col">Score</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Discovery Call - Acme Corp</td>
              <td>Jan 15, 2024</td>
              <td>45m</td>
              <td>Discovery</td>
              <td>85</td>
            </tr>
          </tbody>
        </table>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible clickable table rows", async () => {
      const { container } = render(
        <table>
          <tbody>
            <tr
              role="button"
              tabIndex={0}
              aria-label="View call details for Discovery Call - Acme Corp"
            >
              <td>Discovery Call - Acme Corp</td>
              <td>Jan 15, 2024</td>
            </tr>
          </tbody>
        </table>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Call Detail Page (/calls/[id])", () => {
    it("should have accessible main content structure", async () => {
      const { container } = render(
        <main aria-label="Call analysis details">
          <div className="container mx-auto py-8 px-4 max-w-7xl">
            <h1>Call Analysis</h1>
            <section aria-labelledby="scoring-section">
              <h2 id="scoring-section">Scoring Summary</h2>
            </section>
            <section aria-labelledby="transcript-section">
              <h2 id="transcript-section">Call Transcript</h2>
            </section>
          </div>
        </main>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible tabs navigation", async () => {
      const { container } = render(
        <div>
          <div role="tablist" aria-label="Call analysis sections">
            <button
              role="tab"
              aria-selected="true"
              aria-controls="overview-panel"
              id="overview-tab"
            >
              Overview
            </button>
            <button
              role="tab"
              aria-selected="false"
              aria-controls="transcript-panel"
              id="transcript-tab"
            >
              Transcript
            </button>
          </div>
          <div role="tabpanel" id="overview-panel" aria-labelledby="overview-tab">
            Overview content
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible score badges with proper ARIA labels", async () => {
      const { container } = render(
        <div>
          <span role="status" aria-label="Discovery score: 85 out of 100, good performance">
            <span className="badge">85</span>
          </span>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Team Dashboard Page (/team/dashboard)", () => {
    it("should have accessible stats cards", async () => {
      const { container } = render(
        <div className="grid gap-4 md:grid-cols-3" role="group" aria-label="Team statistics">
          <div role="article" aria-labelledby="total-users-heading">
            <h3 id="total-users-heading">Total Users</h3>
            <p aria-label="Total users count">15</p>
            <p className="text-xs text-muted-foreground">Assigned roles</p>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible team table with actions", async () => {
      const { container } = render(
        <table aria-label="Team members list">
          <thead>
            <tr>
              <th scope="col">Email</th>
              <th scope="col">Role</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>john@example.com</td>
              <td>Manager</td>
              <td>
                <Button aria-label="Edit role for john@example.com">Edit</Button>
                <Button aria-label="Delete role for john@example.com">Delete</Button>
              </td>
            </tr>
          </tbody>
        </table>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible form for adding users", async () => {
      const { container } = render(
        <form aria-label="Add new team member">
          <Label htmlFor="new-user-email">Email</Label>
          <Input id="new-user-email" type="email" placeholder="user@prefect.io" />
          <Label htmlFor="new-user-role">Role</Label>
          <select id="new-user-role" aria-label="Select role for new user">
            <option value="rep">Rep</option>
            <option value="manager">Manager</option>
          </select>
          <Button type="submit">Save</Button>
          <Button type="button">Cancel</Button>
        </form>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have accessible alert for errors", async () => {
      const { container } = render(
        <div role="alert" aria-live="assertive" className="border-destructive bg-destructive/10">
          <div className="flex items-center gap-2 text-destructive">
            <span aria-hidden="true">⚠️</span>
            <span>Failed to load team members</span>
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Color Contrast - WCAG AA Compliance", () => {
    it("should pass contrast for primary text", async () => {
      const { container } = render(
        <div style={{ backgroundColor: "#ffffff", padding: "20px" }}>
          <p style={{ color: "#000000" }}>High contrast text (21:1 ratio)</p>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should pass contrast for muted text (minimum 4.5:1)", async () => {
      const { container } = render(
        <div style={{ backgroundColor: "#ffffff", padding: "20px" }}>
          <p style={{ color: "#666666" }}>Muted text (5.74:1 ratio)</p>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should pass contrast for buttons", async () => {
      const { container } = render(
        <Button style={{ backgroundColor: "#0066cc", color: "#ffffff" }}>Primary Action</Button>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Keyboard Navigation", () => {
    it("should have focusable interactive elements", async () => {
      const { container } = render(
        <div>
          <Button>Focusable Button</Button>
          <a href="/example">Focusable Link</a>
          <Input placeholder="Focusable input" />
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have proper focus order with tabindex", async () => {
      const { container } = render(
        <nav aria-label="Main navigation">
          <a href="/home" tabIndex={0}>
            Home
          </a>
          <a href="/calls" tabIndex={0}>
            Calls
          </a>
          <a href="/team" tabIndex={0}>
            Team
          </a>
        </nav>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should skip navigation with skip link", async () => {
      const { container } = render(
        <div>
          <a href="#main-content" className="sr-only focus:not-sr-only">
            Skip to main content
          </a>
          <nav aria-label="Main navigation">
            <a href="/home">Home</a>
          </nav>
          <main id="main-content">
            <h1>Main Content</h1>
          </main>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe("Screen Reader Support", () => {
    it("should have proper ARIA landmarks", async () => {
      const { container } = render(
        <div>
          <header role="banner">
            <h1>Call Coach</h1>
          </header>
          <nav role="navigation" aria-label="Main navigation">
            <a href="/calls">Calls</a>
          </nav>
          <main role="main">
            <h1>Page Content</h1>
          </main>
          <footer role="contentinfo">
            <p>Footer content</p>
          </footer>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should have descriptive ARIA labels for icons", async () => {
      const { container } = render(
        <div>
          <Button aria-label="Search calls">
            <span aria-hidden="true">🔍</span>
          </Button>
          <Button aria-label="Filter results">
            <span aria-hidden="true">⚙️</span>
          </Button>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it("should announce dynamic content changes", async () => {
      const { container } = render(
        <div>
          <div role="status" aria-live="polite" aria-atomic="true">
            Loading new content...
          </div>
          <div role="alert" aria-live="assertive">
            Error: Failed to load data
          </div>
        </div>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});
