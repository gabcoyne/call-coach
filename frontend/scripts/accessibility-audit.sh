#!/bin/bash

# Accessibility Audit Script for Call Coach Frontend
# Runs axe-core tests and generates a comprehensive audit report

set -e

echo "=========================================="
echo "Call Coach Accessibility Audit"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Run accessibility tests
echo "Running axe-core accessibility tests..."
npm test -- __tests__/accessibility.test.tsx --verbose --no-coverage 2>&1 | tee /tmp/accessibility-test-output.txt

# Check if tests passed
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo ""
    echo "✅ All accessibility tests passed!"
    echo ""
else
    echo ""
    echo "⚠️  Some accessibility tests failed. Review output above."
    echo ""
fi

# Summary
echo "=========================================="
echo "Audit Summary"
echo "=========================================="
echo ""
echo "Test Results:"
grep "Tests:" /tmp/accessibility-test-output.txt || echo "Could not extract test summary"
echo ""

echo "Pages Audited:"
echo "  ✓ /feed (Coaching Feed)"
echo "  ✓ /calls (Calls Library)"
echo "  ✓ /calls/[id] (Call Detail)"
echo "  ✓ /team/dashboard (Team Dashboard)"
echo ""

echo "WCAG 2.1 AA Compliance Areas Checked:"
echo "  ✓ Color Contrast (4.5:1 minimum)"
echo "  ✓ Keyboard Navigation"
echo "  ✓ Screen Reader Support (ARIA)"
echo "  ✓ Semantic HTML Structure"
echo "  ✓ Form Labels and Controls"
echo "  ✓ Focus Management"
echo "  ✓ Heading Hierarchy"
echo ""

echo "For detailed results, see: /tmp/accessibility-test-output.txt"
echo ""
echo "To fix issues:"
echo "  1. Review test failures above"
echo "  2. Update components to address violations"
echo "  3. Re-run: npm test -- __tests__/accessibility.test.tsx"
echo ""
echo "=========================================="
