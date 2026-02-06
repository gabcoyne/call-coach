/**
 * K6 Load Test Script for Call Coach API Routes
 *
 * Prerequisites:
 * - Install k6: brew install k6 (macOS) or see https://k6.io/docs/getting-started/installation/
 * - Ensure Next.js dev server is running: npm run dev
 * - Set environment variables (if needed)
 *
 * Usage:
 * k6 run load-test.k6.js
 *
 * Test Scenarios:
 * - 50 concurrent users for 30 seconds
 * - Tests multiple API endpoints
 * - Measures response times and error rates
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const analyzeCallDuration = new Trend("analyze_call_duration");
const repInsightsDuration = new Trend("rep_insights_duration");
const searchCallsDuration = new Trend("search_calls_duration");

// Test configuration
export const options = {
  stages: [
    { duration: "10s", target: 10 }, // Ramp up to 10 users
    { duration: "20s", target: 50 }, // Ramp up to 50 users
    { duration: "30s", target: 50 }, // Stay at 50 users
    { duration: "10s", target: 0 }, // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"], // 95% < 500ms, 99% < 1s
    http_req_failed: ["rate<0.01"], // Error rate < 1%
    errors: ["rate<0.01"], // Custom error rate < 1%
  },
};

// Base URL (change for production testing)
const BASE_URL = __ENV.BASE_URL || "http://localhost:3000";

// Test data
const testCallIds = ["call-123", "call-456", "call-789"];

const testRepEmails = ["rep1@example.com", "rep2@example.com", "rep3@example.com"];

// Helper to get random item from array
function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export default function () {
  // Randomly select which endpoint to test (simulate real usage)
  const scenario = Math.random();

  if (scenario < 0.4) {
    // 40% - Test analyze call endpoint
    testAnalyzeCall();
  } else if (scenario < 0.7) {
    // 30% - Test rep insights endpoint
    testRepInsights();
  } else {
    // 30% - Test search calls endpoint
    testSearchCalls();
  }

  // Random think time between 1-3 seconds
  sleep(Math.random() * 2 + 1);
}

function testAnalyzeCall() {
  const callId = randomItem(testCallIds);
  const url = `${BASE_URL}/api/coaching/analyze-call`;

  const payload = JSON.stringify({
    call_id: callId,
    dimensions: ["Discovery", "Value Proposition"],
    use_cache: true,
    include_transcript_snippets: false,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
    tags: { name: "AnalyzeCall" },
  };

  const response = http.post(url, payload, params);

  // Record metrics
  analyzeCallDuration.add(response.timings.duration);

  // Validate response
  const success = check(response, {
    "status is 200": (r) => r.status === 200,
    "response has call_id": (r) => JSON.parse(r.body).call_id !== undefined,
    "response has scores": (r) => JSON.parse(r.body).scores !== undefined,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);

  if (response.status !== 200) {
    console.error(`AnalyzeCall failed: ${response.status} - ${response.body}`);
  }
}

function testRepInsights() {
  const repEmail = randomItem(testRepEmails);
  const url = `${BASE_URL}/api/coaching/rep-insights`;

  const payload = JSON.stringify({
    rep_email: repEmail,
    time_period: "last_30_days",
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
    tags: { name: "RepInsights" },
  };

  const response = http.post(url, payload, params);

  // Record metrics
  repInsightsDuration.add(response.timings.duration);

  // Validate response
  const success = check(response, {
    "status is 200": (r) => r.status === 200,
    "response has rep_info": (r) => JSON.parse(r.body).rep_info !== undefined,
    "response has score_trends": (r) => JSON.parse(r.body).score_trends !== undefined,
    "response time < 1s": (r) => r.timings.duration < 1000,
  });

  errorRate.add(!success);

  if (response.status !== 200) {
    console.error(`RepInsights failed: ${response.status} - ${response.body}`);
  }
}

function testSearchCalls() {
  const url = `${BASE_URL}/api/coaching/search-calls`;

  const payload = JSON.stringify({
    product: "prefect",
    limit: 20,
    min_score: 70,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
    tags: { name: "SearchCalls" },
  };

  const response = http.post(url, payload, params);

  // Record metrics
  searchCallsDuration.add(response.timings.duration);

  // Validate response
  const success = check(response, {
    "status is 200": (r) => r.status === 200,
    "response is array": (r) => Array.isArray(JSON.parse(r.body)),
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);

  if (response.status !== 200) {
    console.error(`SearchCalls failed: ${response.status} - ${response.body}`);
  }
}

// Setup function (runs once at start)
export function setup() {
  console.log(`Starting load test against ${BASE_URL}`);
  console.log("Target: 50 concurrent users");
  console.log("Duration: 70 seconds total");

  // Verify server is reachable
  const response = http.get(BASE_URL);
  if (response.status !== 200 && response.status !== 404) {
    throw new Error(`Server not reachable: ${response.status}`);
  }
}

// Teardown function (runs once at end)
export function teardown(data) {
  console.log("Load test complete");
}

// Handle summary output
export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: " ", enableColors: true }),
    "load-test-results.json": JSON.stringify(data),
  };
}

// Helper for text summary
function textSummary(data, options) {
  const indent = options.indent || "";
  const enableColors = options.enableColors || false;

  let output = `${indent}Load Test Summary\n${indent}================\n\n`;

  // Request metrics
  output += `${indent}Requests:\n`;
  output += `${indent}  Total: ${data.metrics.http_reqs.values.count}\n`;
  output += `${indent}  Failed: ${data.metrics.http_req_failed.values.rate * 100}%\n\n`;

  // Response time metrics
  output += `${indent}Response Times:\n`;
  output += `${indent}  Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
  output += `${indent}  Min: ${data.metrics.http_req_duration.values.min.toFixed(2)}ms\n`;
  output += `${indent}  Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
  output += `${indent}  p(90): ${data.metrics.http_req_duration.values["p(90)"].toFixed(2)}ms\n`;
  output += `${indent}  p(95): ${data.metrics.http_req_duration.values["p(95)"].toFixed(2)}ms\n`;
  output += `${indent}  p(99): ${data.metrics.http_req_duration.values["p(99)"].toFixed(2)}ms\n\n`;

  // Threshold results
  output += `${indent}Thresholds:\n`;
  for (const [name, threshold] of Object.entries(data.thresholds)) {
    const passed = threshold.ok ? "✓" : "✗";
    output += `${indent}  ${passed} ${name}\n`;
  }

  return output;
}
