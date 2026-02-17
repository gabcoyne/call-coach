#!/usr/bin/env npx tsx
/**
 * Type Generation Script
 *
 * Generates TypeScript types from the FastAPI OpenAPI schema.
 * This ensures frontend types stay in sync with backend Pydantic models.
 *
 * Usage:
 *   npm run generate:types          # Generate types from running server
 *   npm run generate:types:ci       # Generate from saved schema (CI)
 *
 * The generated types are written to:
 *   frontend/types/generated/api.ts
 */

import { exec } from "child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { promisify } from "util";

const execAsync = promisify(exec);

const API_URL = process.env.API_URL || "http://localhost:8000";
const OPENAPI_ENDPOINT = `${API_URL}/openapi.json`;
const SCHEMA_PATH = join(__dirname, "../openapi.json");
const OUTPUT_DIR = join(__dirname, "../frontend/types/generated");
const OUTPUT_FILE = join(OUTPUT_DIR, "api.ts");

async function fetchOpenAPISchema(): Promise<object> {
  console.log(`📡 Fetching OpenAPI schema from ${OPENAPI_ENDPOINT}...`);

  try {
    const response = await fetch(OPENAPI_ENDPOINT);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const schema = await response.json();
    console.log("✅ Schema fetched successfully");

    // Save schema for CI builds
    writeFileSync(SCHEMA_PATH, JSON.stringify(schema, null, 2));
    console.log(`💾 Schema saved to ${SCHEMA_PATH}`);

    return schema;
  } catch (error) {
    console.log("⚠️  Could not fetch from server, trying saved schema...");

    if (existsSync(SCHEMA_PATH)) {
      const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8"));
      console.log(`✅ Loaded schema from ${SCHEMA_PATH}`);
      return schema;
    }

    throw new Error(
      `Cannot fetch schema from server and no saved schema exists at ${SCHEMA_PATH}. ` +
        `Start the API server with: uv run python api/rest_server.py`
    );
  }
}

async function generateTypes(schema: object): Promise<void> {
  console.log("\n🔧 Generating TypeScript types...");

  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) {
    mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Write schema to temp file for openapi-typescript
  const tempSchemaPath = join(OUTPUT_DIR, "_openapi.json");
  writeFileSync(tempSchemaPath, JSON.stringify(schema, null, 2));

  try {
    // Run openapi-typescript
    const { stdout, stderr } = await execAsync(
      `npx openapi-typescript ${tempSchemaPath} -o ${OUTPUT_FILE}`,
      { cwd: join(__dirname, "../frontend") }
    );

    if (stderr && !stderr.includes("warning")) {
      console.error("stderr:", stderr);
    }

    console.log(`✅ Types generated at ${OUTPUT_FILE}`);

    // Add header comment and re-exports
    const generatedContent = readFileSync(OUTPUT_FILE, "utf-8");
    const enhancedContent = `/**
 * AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
 *
 * This file is generated from the FastAPI OpenAPI schema.
 * To regenerate, run: npm run generate:types
 *
 * Source: ${API_URL}/openapi.json
 * Generated: ${new Date().toISOString()}
 */

${generatedContent}

// ============================================================================
// TYPE ALIASES FOR CONVENIENCE
// ============================================================================

// Request Types (generated from Pydantic models in api/rest_server.py)
export type AnalyzeCallRequest = components["schemas"]["AnalyzeCallRequest"];
export type RepInsightsRequest = components["schemas"]["RepInsightsRequest"];
export type SearchCallsRequest = components["schemas"]["SearchCallsRequest"];
export type AnalyzeOpportunityRequest = components["schemas"]["AnalyzeOpportunityRequest"];
export type LearningInsightsRequest = components["schemas"]["LearningInsightsRequest"];
export type CoachingFeedRequest = components["schemas"]["CoachingFeedRequest"];

// Note: Response types and enums are NOT auto-generated because FastAPI endpoints
// return dict[str, Any]. Response types are defined in types/coaching.ts.
`;

    writeFileSync(OUTPUT_FILE, enhancedContent);
    console.log("✅ Added type aliases and header");
  } finally {
    // Clean up temp file
    if (existsSync(tempSchemaPath)) {
      const { unlinkSync } = await import("fs");
      unlinkSync(tempSchemaPath);
    }
  }
}

async function verifyTypes(): Promise<void> {
  console.log("\n🔍 Verifying generated types...");

  try {
    await execAsync(`npx tsc --noEmit ${OUTPUT_FILE}`, {
      cwd: join(__dirname, "../frontend"),
    });
    console.log("✅ Types are valid TypeScript");
  } catch (error) {
    console.warn("⚠️  Type verification had issues (may be expected for partial schemas)");
  }
}

async function main(): Promise<void> {
  console.log("🚀 Call Coach Type Generator\n");
  console.log("=".repeat(60));

  try {
    const schema = await fetchOpenAPISchema();
    await generateTypes(schema);
    await verifyTypes();

    console.log("\n" + "=".repeat(60));
    console.log("✅ Type generation complete!");
    console.log("\nNext steps:");
    console.log("  1. Import types from 'types/generated/api'");
    console.log("  2. Replace manual type definitions with generated ones");
    console.log("  3. Run: npm run type-check");
  } catch (error) {
    console.error("\n❌ Type generation failed:", error);
    process.exit(1);
  }
}

main();
