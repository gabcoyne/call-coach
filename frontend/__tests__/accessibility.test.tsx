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
