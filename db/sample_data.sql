-- Sample data for testing opportunity coaching UI
-- This simulates real Gong data structure

-- Sample opportunities
INSERT INTO opportunities (id, gong_opportunity_id, name, account_name, owner_email, stage, close_date, amount, health_score, metadata, created_at, updated_at) VALUES
('a0000000-0000-0000-0000-000000000001', 'gong-opp-001', 'Acme Corp - Enterprise Platform', 'Acme Corporation', 'sarah.chen@prefect.io', 'Discovery', '2026-03-15', 125000, 72, '{"source": "salesforce", "probability": 60}', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('a0000000-0000-0000-0000-000000000002', 'gong-opp-002', 'TechStart Inc - Workflow Automation', 'TechStart Inc', 'mike.rodriguez@prefect.io', 'Demo', '2026-04-01', 85000, 45, '{"source": "salesforce", "probability": 40}', NOW() - INTERVAL '45 days', NOW() - INTERVAL '2 days'),
('a0000000-0000-0000-0000-000000000003', 'gong-opp-003', 'DataFlow Systems - Data Pipeline', 'DataFlow Systems', 'sarah.chen@prefect.io', 'Negotiation', '2026-02-28', 200000, 85, '{"source": "salesforce", "probability": 80}', NOW() - INTERVAL '60 days', NOW()),
('a0000000-0000-0000-0000-000000000004', 'gong-opp-004', 'CloudNative Co - Kubernetes Integration', 'CloudNative Co', 'alex.kim@prefect.io', 'Closed Won', '2026-01-31', 150000, 95, '{"source": "salesforce", "probability": 100}', NOW() - INTERVAL '90 days', NOW() - INTERVAL '5 days'),
('a0000000-0000-0000-0000-000000000005', 'gong-opp-005', 'RetailMax - Real-time Analytics', 'RetailMax', 'mike.rodriguez@prefect.io', 'Discovery', '2026-05-15', 95000, 38, '{"source": "salesforce", "probability": 30}', NOW() - INTERVAL '15 days', NOW() - INTERVAL '1 day');

-- Sample calls (some already exist, some new)
INSERT INTO calls (id, gong_call_id, title, scheduled_at, duration_seconds, call_type, product, metadata) VALUES
('c0000000-0000-0000-0000-000000000001', 'gong-call-001', 'Acme Discovery Call - Q1 Goals', NOW() - INTERVAL '25 days', 2700, 'discovery', 'prefect', '{"recording_url": "https://gong.io/calls/001"}'),
('c0000000-0000-0000-0000-000000000002', 'gong-call-002', 'Acme Technical Deep Dive', NOW() - INTERVAL '18 days', 3600, 'technical', 'both', '{"recording_url": "https://gong.io/calls/002"}'),
('c0000000-0000-0000-0000-000000000003', 'gong-call-003', 'TechStart Initial Outreach', NOW() - INTERVAL '40 days', 1800, 'discovery', 'prefect', '{"recording_url": "https://gong.io/calls/003"}'),
('c0000000-0000-0000-0000-000000000004', 'gong-call-004', 'TechStart Product Demo', NOW() - INTERVAL '20 days', 3000, 'demo', 'horizon', '{"recording_url": "https://gong.io/calls/004"}'),
('c0000000-0000-0000-0000-000000000005', 'gong-call-005', 'DataFlow Discovery - Data Pipelines', NOW() - INTERVAL '55 days', 2400, 'discovery', 'prefect', '{"recording_url": "https://gong.io/calls/005"}'),
('c0000000-0000-0000-0000-000000000006', 'gong-call-006', 'DataFlow Technical Architecture Review', NOW() - INTERVAL '35 days', 4200, 'technical', 'prefect', '{"recording_url": "https://gong.io/calls/006"}'),
('c0000000-0000-0000-0000-000000000007', 'gong-call-007', 'DataFlow Pricing Discussion', NOW() - INTERVAL '10 days', 2100, 'negotiation', 'both', '{"recording_url": "https://gong.io/calls/007"}'),
('c0000000-0000-0000-0000-000000000008', 'gong-call-008', 'CloudNative Discovery Call', NOW() - INTERVAL '85 days', 2000, 'discovery', 'prefect', '{"recording_url": "https://gong.io/calls/008"}'),
('c0000000-0000-0000-0000-000000000009', 'gong-call-009', 'CloudNative POC Planning', NOW() - INTERVAL '45 days', 3300, 'technical', 'prefect', '{"recording_url": "https://gong.io/calls/009"}'),
('c0000000-0000-0000-0000-000000000010', 'gong-call-010', 'CloudNative Final Contract Review', NOW() - INTERVAL '10 days', 1500, 'negotiation', 'prefect', '{"recording_url": "https://gong.io/calls/010"}')
ON CONFLICT (gong_call_id) DO NOTHING;

-- Link calls to opportunities
INSERT INTO call_opportunities (call_id, opportunity_id) VALUES
('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
('c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001'),
('c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002'),
('c0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000002'),
('c0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003'),
('c0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003'),
('c0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000003'),
('c0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000004'),
('c0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000004'),
('c0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000004')
ON CONFLICT DO NOTHING;

-- Sample emails
INSERT INTO emails (id, gong_email_id, opportunity_id, subject, sender_email, recipients, sent_at, body_snippet, metadata) VALUES
('e0000000-0000-0000-0000-000000000001', 'gong-email-001', 'a0000000-0000-0000-0000-000000000001', 'Re: Acme Enterprise Platform - Next Steps', 'sarah.chen@prefect.io', ARRAY['john.smith@acme.com', 'jane.doe@acme.com'], NOW() - INTERVAL '20 days', 'Hi John and Jane, Following up on our discovery call last week. I wanted to share some resources about how Prefect handles the specific workflow orchestration challenges you mentioned...', '{"thread_id": "thread-001"}'),
('e0000000-0000-0000-0000-000000000002', 'gong-email-002', 'a0000000-0000-0000-0000-000000000001', 'Acme - Technical Architecture Proposal', 'sarah.chen@prefect.io', ARRAY['john.smith@acme.com'], NOW() - INTERVAL '15 days', 'Hi John, Attached is the technical architecture proposal we discussed. This outlines how Prefect would integrate with your existing data stack (Snowflake, dbt, Airflow migration path)...', '{"thread_id": "thread-001", "has_attachment": true}'),
('e0000000-0000-0000-0000-000000000003', 'gong-email-003', 'a0000000-0000-0000-0000-000000000002', 'TechStart - Demo Recording and Follow-up', 'mike.rodriguez@prefect.io', ARRAY['lisa.wong@techstart.com'], NOW() - INTERVAL '18 days', 'Hi Lisa, Great connecting today! Here is the demo recording link and the ROI calculator we discussed. Based on your current manual workflow processes...', '{"thread_id": "thread-002"}'),
('e0000000-0000-0000-0000-000000000004', 'gong-email-004', 'a0000000-0000-0000-0000-000000000003', 'DataFlow - Pricing and Timeline', 'sarah.chen@prefect.io', ARRAY['robert.chen@dataflow.com'], NOW() - INTERVAL '8 days', 'Hi Robert, Per our conversation, here is the detailed pricing breakdown for the DataFlow implementation. Given your Q1 timeline, we can start the POC in two weeks...', '{"thread_id": "thread-003"}'),
('e0000000-0000-0000-0000-000000000005', 'gong-email-005', 'a0000000-0000-0000-0000-000000000004', 'CloudNative - Contract Executed!', 'alex.kim@prefect.io', ARRAY['david.park@cloudnative.com'], NOW() - INTERVAL '8 days', 'Hi David, Fantastic news - contract is fully executed! Our implementation team will reach out tomorrow to schedule the kickoff call. Looking forward to a successful partnership...', '{"thread_id": "thread-004"}');

-- Sample speakers for calls
INSERT INTO speakers (id, call_id, name, email, role, company_side, talk_time_seconds, talk_time_percentage) VALUES
-- Acme Call 1
('s0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'Sarah Chen', 'sarah.chen@prefect.io', 'ae', true, 1350, 50),
('s0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001', 'John Smith', 'john.smith@acme.com', 'customer', false, 1350, 50),
-- Acme Call 2
('s0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000002', 'Sarah Chen', 'sarah.chen@prefect.io', 'ae', true, 1800, 50),
('s0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000002', 'John Smith', 'john.smith@acme.com', 'customer', false, 1800, 50),
-- TechStart Call 1
('s0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000003', 'Mike Rodriguez', 'mike.rodriguez@prefect.io', 'ae', true, 1080, 60),
('s0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000003', 'Lisa Wong', 'lisa.wong@techstart.com', 'prospect', false, 720, 40),
-- TechStart Call 2
('s0000000-0000-0000-0000-000000000007', 'c0000000-0000-0000-0000-000000000004', 'Mike Rodriguez', 'mike.rodriguez@prefect.io', 'ae', true, 1200, 40),
('s0000000-0000-0000-0000-000000000008', 'c0000000-0000-0000-0000-000000000004', 'Lisa Wong', 'lisa.wong@techstart.com', 'prospect', false, 1800, 60)
ON CONFLICT DO NOTHING;

-- Sample transcripts (abbreviated for brevity)
INSERT INTO transcripts (id, call_id, speaker_id, sequence_number, timestamp_seconds, text, sentiment) VALUES
('t0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000001', 1, 0, 'Hi John, thanks for taking the time today. I know you mentioned on our initial call that your team is struggling with orchestrating complex data pipelines across multiple systems.', 'neutral'),
('t0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000002', 2, 15, 'Yes, exactly. We are currently using Airflow but it has become a bottleneck. We have about 200 DAGs and the development velocity has slowed down significantly.', 'negative'),
('t0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000001', 3, 45, 'That is a common challenge. Can you walk me through a specific example of a pipeline that has been problematic? What does the workflow look like and where does it break down?', 'neutral'),
('t0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000002', 4, 90, 'We have a customer analytics pipeline that pulls from Salesforce, enriches with data from our app database, runs ML models, and pushes to Snowflake. When any step fails, the retry logic is really brittle and we often have to manually intervene.', 'negative')
ON CONFLICT DO NOTHING;

-- Sample coaching sessions for closed-won opportunity (CloudNative - for learning insights)
INSERT INTO coaching_sessions (id, call_id, rep_id, coaching_dimension, session_type, analyst, score, strengths, areas_for_improvement, full_analysis) VALUES
('cs000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000008', 's0000000-0000-0000-0000-000000000001', 'discovery', 'on_demand', 'claude-sonnet-4.5', 92,
 ARRAY['Asked open-ended questions about pain points', 'Actively listened and paraphrased customer needs', 'Identified budget timeline early'],
 ARRAY['Could have probed deeper on decision-making process'],
 'Strong discovery call with excellent questioning technique. Rep established clear pain points and timeline.'),

('cs000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000008', 's0000000-0000-0000-0000-000000000001', 'product_knowledge', 'on_demand', 'claude-sonnet-4.5', 88,
 ARRAY['Accurately explained Prefect architecture', 'Positioned Horizon correctly for use case', 'Drew clear comparisons to Airflow'],
 ARRAY['Missed opportunity to mention new Kubernetes features'],
 'Solid product knowledge with accurate technical details. Effectively differentiated from competitors.')
ON CONFLICT DO NOTHING;
