# Specification

## ADDED Requirements

### Requirement: Comprehensive CLAUDE.md at project root

The system SHALL provide a comprehensive CLAUDE.md file at project root that serves as the single source of truth for backend development.

#### Scenario: CLAUDE.md contains Quick Start section

- **WHEN** developer opens CLAUDE.md
- **THEN** Quick Start section shows how to start server in under 5 minutes
- **THEN** section includes: install uv, clone repo, copy .env, run server command

#### Scenario: CLAUDE.md contains Architecture section

- **WHEN** developer reads Architecture section
- **THEN** section explains FastMCP server structure and tool organization
- **THEN** section documents database schema and key tables
- **THEN** section shows how tools interact with Gong API and database

#### Scenario: CLAUDE.md contains Development Workflow section

- **WHEN** developer reads Development Workflow
- **THEN** section documents Edit → Test → Debug cycle
- **THEN** section shows how to add new tools
- **THEN** section explains how to test tools manually

#### Scenario: CLAUDE.md contains Testing section

- **WHEN** developer reads Testing section
- **THEN** section explains how to run unit tests with pytest
- **THEN** section documents integration testing with real database
- **THEN** section shows how to test individual tools via MCP protocol

#### Scenario: CLAUDE.md contains Troubleshooting section

- **WHEN** developer encounters common errors
- **THEN** Troubleshooting section lists errors with solutions
- **THEN** section covers: missing env vars, database connection issues, API rate limits

#### Scenario: CLAUDE.md contains Deployment section

- **WHEN** developer prepares for Horizon deployment
- **THEN** Deployment section documents differences from local dev
- **THEN** section explains environment variable configuration in Horizon UI
- **THEN** section covers validation requirements for production

### Requirement: Updated README with local development quick-start

The root README.md SHALL include a Local Development section that links to CLAUDE.md for detailed instructions.

#### Scenario: README contains Local Development section

- **WHEN** developer opens root README.md
- **THEN** Local Development section provides 3-step quick start
- **THEN** section links to CLAUDE.md for comprehensive guide

### Requirement: Full-stack local testing documentation

The documentation SHALL explain how to run frontend, backend, and database together for local integration testing.

#### Scenario: Documentation shows three-terminal setup

- **WHEN** developer needs to test full stack locally
- **THEN** CLAUDE.md shows Terminal 1: backend with `uv run mcp-server-dev`
- **THEN** CLAUDE.md shows Terminal 2: frontend with `cd frontend && npm run dev`
- **THEN** CLAUDE.md shows Terminal 3: database already running (Neon cloud)

#### Scenario: Documentation explains frontend-backend connection

- **WHEN** developer tests API calls from frontend
- **THEN** documentation explains NEXT_PUBLIC_MCP_BACKEND_URL configuration
- **THEN** documentation shows how to verify tools are callable from frontend
- **THEN** documentation includes example API request/response

### Requirement: Environment variable documentation

The documentation SHALL provide complete reference for all environment variables with examples and sources.

#### Scenario: CLAUDE.md documents required variables

- **WHEN** developer sets up .env file
- **THEN** documentation lists all required variables with descriptions
- **THEN** documentation shows where to obtain API keys (Gong dashboard, Anthropic, Neon)
- **THEN** documentation includes complete .env.example with placeholders

### Requirement: Common pitfalls and solutions

The documentation SHALL anticipate and document common development issues with solutions.

#### Scenario: Documentation covers missing .env error

- **WHEN** server fails with "Missing required environment variables"
- **THEN** Troubleshooting section explains .env must be in project root
- **THEN** section shows how to verify .env location with ls command

#### Scenario: Documentation covers database connection errors

- **WHEN** server fails with database connection error
- **THEN** Troubleshooting section explains sslmode=require requirement for Neon
- **THEN** section shows how to test connection with psql command
- **THEN** section includes instructions for checking Neon dashboard

#### Scenario: Documentation covers port conflicts

- **WHEN** server fails to start on port 8000
- **THEN** Troubleshooting section explains how to check for port conflicts
- **THEN** section shows how to kill existing process or use different port
