-- Migration: 013_seed_rubric_criteria.sql
-- Purpose: Seed default rubric criteria for all role-dimension combinations
-- Date: 2026-02-07
-- Roles: ae (Account Executive), se (Sales Engineer), csm (Customer Success Manager), support (Support Engineer)
-- Dimensions: discovery, engagement, product_knowledge, objection_handling, five_wins

-- Clear any existing criteria (for idempotency)
DELETE FROM rubric_criteria;

-- ============================================================
-- AE (Account Executive) Rubric Criteria
-- ============================================================

-- AE Discovery Criteria (6 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('ae', 'discovery', 'Opening Questions', 'Quality and effectiveness of opening questions to understand customer needs', 15, 10, 1),
('ae', 'discovery', 'SPICED Framework', 'Application of SPICED (Situation, Pain, Impact, Critical Event, Decision) discovery framework', 25, 10, 2),
('ae', 'discovery', 'Pain Identification', 'Ability to identify and articulate customer pain points', 20, 10, 3),
('ae', 'discovery', 'Impact Quantification', 'Effectiveness in quantifying business impact and ROI', 20, 10, 4),
('ae', 'discovery', 'Decision Process', 'Understanding of customer decision-making process and stakeholders', 10, 10, 5),
('ae', 'discovery', 'Budget Exploration', 'Tactful exploration of budget and procurement requirements', 10, 10, 6);

-- AE Engagement Criteria (5 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('ae', 'engagement', 'Talk-Listen Ratio', 'Maintaining appropriate 30:70 talk-to-listen ratio for discovery', 25, 10, 1),
('ae', 'engagement', 'Active Listening', 'Demonstrating active listening through follow-up questions and summaries', 25, 10, 2),
('ae', 'engagement', 'Rapport Building', 'Building trust and rapport with customer stakeholders', 20, 10, 3),
('ae', 'engagement', 'Energy Level', 'Maintaining appropriate energy and enthusiasm throughout call', 15, 10, 4),
('ae', 'engagement', 'Objection Handling', 'Grace and effectiveness in handling customer objections', 15, 10, 5);

-- AE Product Knowledge Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('ae', 'product_knowledge', 'Value Proposition', 'Clarity and effectiveness of value proposition articulation', 30, 10, 1),
('ae', 'product_knowledge', 'Feature-Benefit Mapping', 'Connecting product features to customer-specific benefits', 30, 10, 2),
('ae', 'product_knowledge', 'Competitive Positioning', 'Understanding and articulating competitive advantages', 20, 10, 3),
('ae', 'product_knowledge', 'Use Case Relevance', 'Presenting relevant use cases and success stories', 20, 10, 4);

-- AE Objection Handling Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('ae', 'objection_handling', 'Acknowledgment', 'Acknowledging and validating customer concerns before responding', 20, 10, 1),
('ae', 'objection_handling', 'Reframing', 'Ability to reframe objections into opportunities', 30, 10, 2),
('ae', 'objection_handling', 'Evidence-Based Response', 'Providing data, case studies, or proof points to address concerns', 30, 10, 3),
('ae', 'objection_handling', 'Follow-Through', 'Committing to follow-up actions and next steps', 20, 10, 4);

-- AE Five Wins Criteria (5 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('ae', 'five_wins', 'Business Win', 'Value proposition, ROI quantification, and business case building', 25, 10, 1),
('ae', 'five_wins', 'Technical Win', 'Demonstrating technical fit and feasibility', 20, 10, 2),
('ae', 'five_wins', 'Commercial Win', 'Pricing discussion, budget fit, and procurement alignment', 25, 10, 3),
('ae', 'five_wins', 'Security Win', 'Addressing security, compliance, and governance requirements', 15, 10, 4),
('ae', 'five_wins', 'Personal Win', 'Connecting solution to personal/career goals of stakeholders', 15, 10, 5);

-- ============================================================
-- SE (Sales Engineer) Rubric Criteria
-- ============================================================

-- SE Discovery Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('se', 'discovery', 'Technical Requirements', 'Understanding technical requirements, constraints, and current architecture', 30, 10, 1),
('se', 'discovery', 'Architecture Fit', 'Assessing how solution fits into customer architecture', 30, 10, 2),
('se', 'discovery', 'Integration Complexity', 'Understanding integration points and technical dependencies', 25, 10, 3),
('se', 'discovery', 'Technical Stakeholder Mapping', 'Identifying and engaging technical decision-makers', 15, 10, 4);

-- SE Engagement Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('se', 'engagement', 'Technical Clarity', 'Explaining complex technical concepts clearly', 30, 10, 1),
('se', 'engagement', 'Stakeholder Engagement', 'Engaging technical stakeholders effectively', 25, 10, 2),
('se', 'engagement', 'Technical Patience', 'Patience and thoroughness during technical deep-dives', 25, 10, 3),
('se', 'engagement', 'Credibility Building', 'Establishing technical credibility and trust', 20, 10, 4);

-- SE Product Knowledge Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('se', 'product_knowledge', 'Technical Architecture', 'Deep understanding of product technical architecture', 35, 10, 1),
('se', 'product_knowledge', 'Integration Capabilities', 'Knowledge of APIs, SDKs, and integration patterns', 30, 10, 2),
('se', 'product_knowledge', 'Scalability & Performance', 'Understanding of performance characteristics and scalability', 20, 10, 3),
('se', 'product_knowledge', 'Technical Roadmap', 'Awareness of technical roadmap and upcoming capabilities', 15, 10, 4);

-- SE Objection Handling Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('se', 'objection_handling', 'Technical Validation', 'Validating technical concerns with data and testing', 35, 10, 1),
('se', 'objection_handling', 'Alternative Solutions', 'Proposing alternative technical approaches', 30, 10, 2),
('se', 'objection_handling', 'Risk Mitigation', 'Addressing technical risks with concrete mitigation plans', 25, 10, 3),
('se', 'objection_handling', 'Escalation Path', 'Knowing when to escalate to product/engineering teams', 10, 10, 4);

-- SE Five Wins Criteria (5 criteria, weights sum to 100, Technical Win higher weight)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('se', 'five_wins', 'Technical Win', 'Demonstrating technical fit, feasibility, and architecture benefits', 35, 10, 1),
('se', 'five_wins', 'Security Win', 'Detailed security, compliance, and governance validation', 25, 10, 2),
('se', 'five_wins', 'Business Win', 'Technical value and operational efficiency benefits', 20, 10, 3),
('se', 'five_wins', 'Integration Win', 'Ease of integration and technical enablement', 15, 10, 4),
('se', 'five_wins', 'Personal Win', 'Technical team enablement and career development', 5, 10, 5);

-- ============================================================
-- CSM (Customer Success Manager) Rubric Criteria
-- ============================================================

-- CSM Discovery Criteria (5 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('csm', 'discovery', 'Relationship Exploration', 'Understanding stakeholder relationships and account dynamics', 20, 10, 1),
('csm', 'discovery', 'Usage Patterns', 'Uncovering product usage patterns and adoption levels', 25, 10, 2),
('csm', 'discovery', 'Expansion Opportunities', 'Identifying opportunities for expansion and upsell', 20, 10, 3),
('csm', 'discovery', 'Health Indicators', 'Assessing account health and engagement levels', 20, 10, 4),
('csm', 'discovery', 'Renewal Risk Factors', 'Identifying potential renewal risks early', 15, 10, 5);

-- CSM Engagement Criteria (5 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('csm', 'engagement', 'Empathy', 'Demonstrating empathy and understanding of customer challenges', 25, 10, 1),
('csm', 'engagement', 'Relationship Depth', 'Building deep, trusted relationships with stakeholders', 25, 10, 2),
('csm', 'engagement', 'Customer Advocacy', 'Acting as customer advocate and trusted advisor', 20, 10, 3),
('csm', 'engagement', 'Proactive Communication', 'Proactively communicating value and addressing concerns', 20, 10, 4),
('csm', 'engagement', 'Trust Building', 'Building long-term trust and partnership', 10, 10, 5);

-- CSM Product Knowledge Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('csm', 'product_knowledge', 'Value Realization', 'Helping customers realize value from product usage', 30, 10, 1),
('csm', 'product_knowledge', 'Best Practices', 'Sharing best practices and optimization strategies', 30, 10, 2),
('csm', 'product_knowledge', 'Feature Adoption', 'Driving adoption of relevant features', 25, 10, 3),
('csm', 'product_knowledge', 'Roadmap Alignment', 'Aligning customer needs with product roadmap', 15, 10, 4);

-- CSM Objection Handling Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('csm', 'objection_handling', 'Issue Acknowledgment', 'Acknowledging and taking ownership of customer issues', 25, 10, 1),
('csm', 'objection_handling', 'Solution Orientation', 'Focusing on solutions and path forward', 30, 10, 2),
('csm', 'objection_handling', 'Escalation Management', 'Managing escalations and internal advocacy', 25, 10, 3),
('csm', 'objection_handling', 'Recovery & Trust Rebuild', 'Rebuilding trust after service issues', 20, 10, 4);

-- CSM Five Wins Criteria (5 criteria, weights sum to 100, adapted to post-sales)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('csm', 'five_wins', 'Business Win', 'Adoption metrics, value realization, and expansion opportunities', 30, 10, 1),
('csm', 'five_wins', 'Renewal Win', 'Positioning for successful renewal and contract health', 30, 10, 2),
('csm', 'five_wins', 'Technical Win', 'Technical adoption and integration success', 15, 10, 3),
('csm', 'five_wins', 'Executive Win', 'Executive sponsorship and strategic alignment', 15, 10, 4),
('csm', 'five_wins', 'Personal Win', 'Customer career success and personal advocacy', 10, 10, 5);

-- ============================================================
-- Support (Support Engineer) Rubric Criteria
-- ============================================================

-- Support Discovery Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('support', 'discovery', 'Issue Identification', 'Quickly and accurately identifying the core issue', 30, 10, 1),
('support', 'discovery', 'Impact Assessment', 'Understanding business impact and urgency', 25, 10, 2),
('support', 'discovery', 'Troubleshooting Methodology', 'Systematic approach to root cause analysis', 30, 10, 3),
('support', 'discovery', 'Environment Understanding', 'Understanding customer environment and configuration', 15, 10, 4);

-- Support Engagement Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('support', 'engagement', 'Responsiveness', 'Timely and attentive response to customer needs', 30, 10, 1),
('support', 'engagement', 'Empathy During Issues', 'Showing empathy during stressful situations', 25, 10, 2),
('support', 'engagement', 'Troubleshooting Patience', 'Patience and clarity during troubleshooting', 25, 10, 3),
('support', 'engagement', 'Technical Communication', 'Clear communication of technical details', 20, 10, 4);

-- Support Product Knowledge Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('support', 'product_knowledge', 'Technical Accuracy', 'Accuracy of technical information and solutions', 35, 10, 1),
('support', 'product_knowledge', 'Troubleshooting Expertise', 'Depth of troubleshooting knowledge and skills', 30, 10, 2),
('support', 'product_knowledge', 'Documentation Usage', 'Effective use and reference to documentation', 20, 10, 3),
('support', 'product_knowledge', 'Known Issues Awareness', 'Awareness of known issues and workarounds', 15, 10, 4);

-- Support Objection Handling Criteria (4 criteria, weights sum to 100)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('support', 'objection_handling', 'Frustration Management', 'Handling customer frustration with professionalism', 30, 10, 1),
('support', 'objection_handling', 'Expectations Setting', 'Setting clear expectations on resolution timeline', 25, 10, 2),
('support', 'objection_handling', 'Workaround Provision', 'Providing effective workarounds when needed', 25, 10, 3),
('support', 'objection_handling', 'Escalation Transparency', 'Transparent communication about escalations', 20, 10, 4);

-- Support Five Wins Criteria (3 criteria, weights sum to 100, simplified for support context)
INSERT INTO rubric_criteria (role, dimension, criterion_name, description, weight, max_score, display_order) VALUES
('support', 'five_wins', 'Issue Resolution', 'Successfully resolving the technical issue', 50, 10, 1),
('support', 'five_wins', 'Customer Satisfaction', 'Ensuring customer satisfaction with support experience', 30, 10, 2),
('support', 'five_wins', 'Technical Accuracy', 'Providing technically accurate solutions and guidance', 20, 10, 3);

-- Show summary
DO $$
DECLARE
    total_criteria INTEGER;
    ae_count INTEGER;
    se_count INTEGER;
    csm_count INTEGER;
    support_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_criteria FROM rubric_criteria;
    SELECT COUNT(*) INTO ae_count FROM rubric_criteria WHERE role = 'ae';
    SELECT COUNT(*) INTO se_count FROM rubric_criteria WHERE role = 'se';
    SELECT COUNT(*) INTO csm_count FROM rubric_criteria WHERE role = 'csm';
    SELECT COUNT(*) INTO support_count FROM rubric_criteria WHERE role = 'support';

    RAISE NOTICE '=== Rubric Criteria Seeded Successfully ===';
    RAISE NOTICE 'Total criteria created: %', total_criteria;
    RAISE NOTICE '';
    RAISE NOTICE 'Criteria by role:';
    RAISE NOTICE '  AE (Account Executive): % criteria', ae_count;
    RAISE NOTICE '  SE (Sales Engineer): % criteria', se_count;
    RAISE NOTICE '  CSM (Customer Success): % criteria', csm_count;
    RAISE NOTICE '  Support: % criteria', support_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Dimensions covered:';
    RAISE NOTICE '  - discovery';
    RAISE NOTICE '  - engagement';
    RAISE NOTICE '  - product_knowledge';
    RAISE NOTICE '  - objection_handling';
    RAISE NOTICE '  - five_wins';
    RAISE NOTICE '';
    RAISE NOTICE 'Next: Verify weights sum to 100%% per role-dimension';
END $$;

-- Validate that all dimension weights sum to 100%
DO $$
DECLARE
    validation_record RECORD;
    has_errors BOOLEAN := false;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== Weight Validation ===';

    FOR validation_record IN
        SELECT
            role,
            dimension,
            SUM(weight) as total_weight
        FROM rubric_criteria
        GROUP BY role, dimension
        ORDER BY role, dimension
    LOOP
        IF validation_record.total_weight != 100 THEN
            RAISE WARNING 'INVALID: % - % weights sum to % (should be 100)',
                validation_record.role,
                validation_record.dimension,
                validation_record.total_weight;
            has_errors := true;
        ELSE
            RAISE NOTICE '✓ % - % weights sum to 100%%',
                validation_record.role,
                validation_record.dimension;
        END IF;
    END LOOP;

    IF NOT has_errors THEN
        RAISE NOTICE '';
        RAISE NOTICE '✓ All dimension weights validate correctly!';
    END IF;
END $$;
