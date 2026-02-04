## ADDED Requirements

### Requirement: Webhook signature verification
The system SHALL verify all incoming Gong webhooks using HMAC-SHA256 signature validation.

#### Scenario: Valid signature
- **WHEN** webhook arrives with correct X-Gong-Signature header
- **THEN** system accepts the webhook and processes it

#### Scenario: Invalid signature
- **WHEN** webhook arrives with incorrect or missing signature
- **THEN** system returns 401 Unauthorized and does not process the webhook

### Requirement: Idempotency
The system SHALL handle duplicate webhook deliveries idempotently using the X-Gong-Webhook-Id header.

#### Scenario: First delivery
- **WHEN** webhook with new X-Gong-Webhook-Id arrives
- **THEN** system stores event and triggers processing

#### Scenario: Duplicate delivery
- **WHEN** webhook with existing X-Gong-Webhook-Id arrives
- **THEN** system returns 200 OK but does not re-process the event

### Requirement: Response time
The webhook endpoint SHALL respond within 500ms to prevent Gong timeouts.

#### Scenario: Fast path
- **WHEN** webhook is received
- **THEN** system validates, stores payload, and returns 200 OK within 500ms

#### Scenario: Async processing
- **WHEN** webhook is accepted
- **THEN** system triggers Prefect flow asynchronously without blocking response

### Requirement: Event storage
The system SHALL store webhook events in database for audit trail and debugging.

#### Scenario: Event persistence
- **WHEN** webhook is received
- **THEN** system stores full payload, timestamp, signature validity, and processing status

### Requirement: Status tracking
The system SHALL track webhook processing status through lifecycle states.

#### Scenario: Status progression
- **WHEN** webhook is received
- **THEN** status transitions: received → processing → completed/failed
- **AND** processed_at timestamp is set on completion
