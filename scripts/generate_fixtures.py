#!/usr/bin/env python3
"""
Generate realistic sample data and fixtures for the call coaching application.

This script creates:
1. Realistic call transcripts (using templates)
2. Sample speakers (AEs, SEs, CSMs with @prefect.io emails)
3. Coaching sessions with varied scores
4. Opportunities with calls linked
5. Emails for opportunities

All data is fully configurable (number of calls, date range, etc.).
"""
import argparse
import logging
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from db import execute_query, execute_many, fetch_all, fetch_one

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "generate_fixtures.log"),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# TEMPLATE DATA
# ============================================================================

FIRST_NAMES = [
    "John", "Sarah", "Mike", "Lisa", "Alex", "Emma", "David", "Jessica",
    "Robert", "Michelle", "James", "Lauren", "Michael", "Amanda", "Christopher"
]

LAST_NAMES = [
    "Smith", "Chen", "Rodriguez", "Kim", "Wong", "Johnson", "Williams",
    "Park", "Patel", "Lee", "Kumar", "Garcia", "Martinez", "Lopez", "Davis"
]

COMPANY_NAMES = [
    "Acme Corporation", "TechStart Inc", "DataFlow Systems", "CloudNative Co",
    "RetailMax", "FinServe Group", "MedicalTech Solutions", "EduPlatform LLC",
    "LogisticsPro Inc", "AnalyticsHub Corp", "SecureNet Systems", "AppBuilder Labs",
    "DataOps Solutions", "CloudFirst Technologies", "InnovateX Partners"
]

CALL_TITLES = [
    "Initial Discovery Call",
    "Product Demo",
    "Technical Deep Dive",
    "Architecture Review",
    "POC Planning",
    "Pricing Discussion",
    "Executive Briefing",
    "Integration Planning",
    "Follow-up Discussion",
    "Requirements Gathering",
    "Implementation Planning",
    "Final Contract Review",
    "Kickoff Call",
    "Success Planning",
    "Quarterly Business Review"
]

COACHING_DIMENSIONS = ["product_knowledge", "discovery", "objection_handling", "engagement"]
SESSION_TYPES = ["real_time", "weekly_review", "on_demand"]

# Realistic call transcript templates
TRANSCRIPT_TEMPLATES = {
    "discovery": [
        {
            "ae": "Hi {prospect_name}, thanks for taking the time today. I know you mentioned on our initial call that your team is struggling with {pain_point_1}.",
            "prospect": "Yes, exactly. We are currently using {current_solution} but it has become {pain_point_2}.",
            "ae": "That is a common challenge. Can you walk me through a specific example of {pain_point_1}? What does the workflow look like?",
            "prospect": "We have a {use_case} pipeline that {detailed_workflow}. When any step fails, {failure_scenario}.",
        },
        {
            "ae": "Tell me about your current data infrastructure. What tools are you using today?",
            "prospect": "We have {tech_stack_1}, {tech_stack_2}, and {tech_stack_3} in our stack.",
            "ae": "How are those systems integrated? What are the pain points?",
            "prospect": "Integration is manual and brittle. We spend too much time on {operational_burden}.",
            "ae": "What's the impact on your business? How much time and resources is this consuming?",
            "prospect": "We estimate we're losing about {time_investment} a week in manual effort.",
        }
    ],
    "demo": [
        {
            "ae": "Let me show you how Prefect handles workflow orchestration. This is our core UI.",
            "prospect": "What makes this different from {competitor_name}?",
            "ae": "Great question. Prefect is {key_diff_1} and {key_diff_2}. Let me show you a real example.",
            "prospect": "That's impressive. How does it handle {technical_concern}?",
            "ae": "Excellent question. It natively supports {technical_answer} out of the box.",
        }
    ],
    "technical": [
        {
            "ae": "Let's dive into the architecture. Here's how Prefect would integrate with {customer_stack}.",
            "prospect": "How does data flow through the system?",
            "ae": "Data flows from {data_source} → Prefect → {data_sink}. We handle retries, error handling, and monitoring automatically.",
            "prospect": "What about disaster recovery and failover?",
            "se": "We have multi-region support, automatic failover, and comprehensive audit logging. Let me show you the architecture diagram.",
        }
    ],
    "negotiation": [
        {
            "ae": "Based on your requirements and usage, here's the pricing model. You'll be in the {tier} tier.",
            "prospect": "What's included in that tier?",
            "ae": "You get {features_1}, {features_2}, and {features_3}. Plus 24/7 support.",
            "prospect": "We need to work within a {budget_constraint} budget.",
            "ae": "I understand. Let me put together a customized proposal that addresses your budget.",
        }
    ]
}

PAIN_POINTS = [
    "orchestrating complex data pipelines across multiple systems",
    "managing dependencies between batch and streaming jobs",
    "handling errors and retries in production workflows",
    "monitoring and alerting on workflow failures",
    "scaling as data volume grows",
    "integrating disparate data sources",
    "managing data quality and validation",
]

SOLUTIONS = ["Airflow", "Dask", "Luigi", "Oozie", "Spark", "custom Python scripts"]
TECH_STACKS = ["Snowflake", "Postgres", "S3", "Kafka", "dbt", "Spark", "Jupyter", "Lambda"]
USE_CASES = ["customer analytics", "ML training", "ETL", "real-time processing", "data migration", "compliance reporting"]

OPPORTUNITY_STAGES = ["Discovery", "Demo", "Technical Deep Dive", "Negotiation", "Closed Won", "Closed Lost"]
OPPORTUNITY_AMOUNTS = [50000, 75000, 100000, 150000, 200000, 250000, 300000]

# ============================================================================
# FIXTURES GENERATOR
# ============================================================================

class FixturesGenerator:
    """Generate realistic sample data for testing."""

    def __init__(self, num_calls: int = 20, days_back: int = 90, seed: int | None = None):
        """
        Initialize the fixtures generator.

        Args:
            num_calls: Number of sample calls to generate
            days_back: How many days back to generate data for
            seed: Random seed for reproducibility
        """
        self.num_calls = num_calls
        self.days_back = days_back
        self.seed = seed

        if seed is not None:
            import random
            random.seed(seed)

        # Track created entities
        self.created_speakers = []
        self.created_calls = []
        self.created_opportunities = []
        self.created_coaching_sessions = []
        self.created_emails = []

    # ========================================================================
    # SPEAKER GENERATION
    # ========================================================================

    def generate_speakers(self) -> list[dict[str, Any]]:
        """Generate sample Prefect employees (AEs, SEs, CSMs)."""
        logger.info("Generating sample speakers...")

        roles_count = {
            "ae": 4,  # Account Executives
            "se": 3,  # Sales Engineers
            "csm": 2,  # Customer Success Managers
        }

        speakers = []
        for role, count in roles_count.items():
            for i in range(count):
                first_name = FIRST_NAMES[i % len(FIRST_NAMES)]
                last_name = LAST_NAMES[i % len(LAST_NAMES)]
                email = f"{first_name.lower()}.{last_name.lower()}@prefect.io"

                speaker = {
                    "id": str(uuid.uuid4()),
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "role": role,
                    "company_side": True,
                }
                speakers.append(speaker)

        logger.info(f"Generated {len(speakers)} speakers")
        self.created_speakers = speakers
        return speakers

    # ========================================================================
    # OPPORTUNITY GENERATION
    # ========================================================================

    def generate_opportunities(self, num_opportunities: int | None = None) -> list[dict[str, Any]]:
        """Generate sample opportunities."""
        if num_opportunities is None:
            num_opportunities = max(3, self.num_calls // 3)

        logger.info(f"Generating {num_opportunities} opportunities...")

        import random

        opportunities = []
        ae_speakers = [s for s in self.created_speakers if s["role"] == "ae"]

        for i in range(num_opportunities):
            company_name = COMPANY_NAMES[i % len(COMPANY_NAMES)]
            owner = random.choice(ae_speakers)

            opp = {
                "id": str(uuid.uuid4()),
                "gong_opportunity_id": f"gong-opp-{i:03d}",
                "name": f"{company_name} - Enterprise Solution",
                "account_name": company_name,
                "owner_email": owner["email"],
                "stage": random.choice(OPPORTUNITY_STAGES),
                "close_date": datetime.now() + timedelta(days=random.randint(7, 120)),
                "amount": random.choice(OPPORTUNITY_AMOUNTS),
                "health_score": random.randint(30, 95),
                "metadata": {
                    "source": "salesforce",
                    "probability": random.randint(30, 100),
                },
            }
            opportunities.append(opp)

        logger.info(f"Generated {len(opportunities)} opportunities")
        self.created_opportunities = opportunities
        return opportunities

    # ========================================================================
    # CALL GENERATION
    # ========================================================================

    def generate_calls(self) -> list[dict[str, Any]]:
        """Generate sample calls with realistic transcripts."""
        logger.info(f"Generating {self.num_calls} calls...")

        import random

        calls = []
        call_types = ["discovery", "demo", "technical_deep_dive", "negotiation", "follow_up"]
        products = ["prefect", "horizon", "both"]

        for i in range(self.num_calls):
            # Random date within range
            days_ago = random.randint(0, self.days_back)
            scheduled_at = datetime.now() - timedelta(days=days_ago)

            call = {
                "id": str(uuid.uuid4()),
                "gong_call_id": f"gong-call-{i:04d}",
                "title": random.choice(CALL_TITLES),
                "scheduled_at": scheduled_at,
                "duration_seconds": random.randint(600, 5400),  # 10-90 minutes
                "call_type": random.choice(call_types),
                "product": random.choice(products),
                "created_at": scheduled_at,
                "processed_at": None,
                "metadata": {
                    "recording_url": f"https://gong.io/calls/{i:04d}",
                    "gong_data": {
                        "attendee_count": random.randint(2, 5),
                    },
                },
            }
            calls.append(call)

        logger.info(f"Generated {len(calls)} calls")
        self.created_calls = calls
        return calls

    # ========================================================================
    # SPEAKER PARTICIPATION GENERATION
    # ========================================================================

    def generate_call_speakers(self) -> list[dict[str, Any]]:
        """Generate speakers for each call."""
        logger.info("Generating call speakers...")

        import random

        speakers_for_calls = []
        ae_speakers = [s for s in self.created_speakers if s["role"] == "ae"]
        se_speakers = [s for s in self.created_speakers if s["role"] == "se"]

        for call in self.created_calls:
            # Add 1-2 Prefect employees
            num_prefect = random.randint(1, 2)
            prefect_reps = random.sample(ae_speakers + se_speakers, num_prefect)

            for rep in prefect_reps:
                speaker = {
                    "id": str(uuid.uuid4()),
                    "call_id": call["id"],
                    "name": rep["name"],
                    "email": rep["email"],
                    "role": rep["role"],
                    "company_side": True,
                    "talk_time_seconds": random.randint(600, 2400),
                    "talk_time_percentage": random.randint(30, 70),
                }
                speakers_for_calls.append(speaker)

            # Add 1-3 prospect/customer participants
            num_prospects = random.randint(1, 3)
            for j in range(num_prospects):
                first_name = FIRST_NAMES[random.randint(0, len(FIRST_NAMES) - 1)]
                last_name = LAST_NAMES[random.randint(0, len(LAST_NAMES) - 1)]
                company = random.choice(COMPANY_NAMES)
                company_domain = company.lower().replace(" ", "").replace("-", "")

                prospect = {
                    "id": str(uuid.uuid4()),
                    "call_id": call["id"],
                    "name": f"{first_name} {last_name}",
                    "email": f"{first_name.lower()}.{last_name.lower()}@{company_domain}.com",
                    "role": random.choice(["prospect", "customer"]),
                    "company_side": False,
                    "talk_time_seconds": random.randint(600, 2400),
                    "talk_time_percentage": random.randint(30, 70),
                }
                speakers_for_calls.append(prospect)

        logger.info(f"Generated {len(speakers_for_calls)} call speaker records")
        return speakers_for_calls

    # ========================================================================
    # TRANSCRIPT GENERATION
    # ========================================================================

    def generate_transcripts(self, speakers_for_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate realistic transcripts for calls."""
        logger.info("Generating transcripts...")

        import random

        transcripts = []
        sequence_num = 0

        for call in self.created_calls:
            # Get speakers for this call
            call_speakers = [s for s in speakers_for_calls if s["call_id"] == call["id"]]
            company_side_speakers = [s for s in call_speakers if s["company_side"]]
            prospect_speakers = [s for s in call_speakers if not s["company_side"]]

            if not company_side_speakers or not prospect_speakers:
                continue

            # Generate 10-20 transcript lines per call
            num_lines = random.randint(10, 20)
            timestamp = 0

            for _ in range(num_lines):
                speaker = random.choice(company_side_speakers + prospect_speakers)
                speaker_id = speaker["id"]

                # Generate realistic transcript text
                text = self._generate_transcript_line(
                    call["call_type"],
                    speaker["company_side"],
                    prospect_speakers[0] if prospect_speakers else None,
                )

                transcript = {
                    "id": str(uuid.uuid4()),
                    "call_id": call["id"],
                    "speaker_id": speaker_id,
                    "sequence_number": sequence_num,
                    "timestamp_seconds": timestamp,
                    "text": text,
                    "sentiment": random.choice(["positive", "neutral", "negative"]),
                    "topics": random.sample(
                        ["pipeline", "orchestration", "data", "performance", "integration", "cost"],
                        k=random.randint(1, 3),
                    ),
                }
                transcripts.append(transcript)

                sequence_num += 1
                timestamp += random.randint(15, 60)

        logger.info(f"Generated {len(transcripts)} transcript lines")
        return transcripts

    def _generate_transcript_line(self, call_type: str, is_company: bool, prospect: dict[str, Any] | None) -> str:
        """Generate a realistic transcript line."""
        import random

        if call_type == "discovery":
            if is_company:
                templates = [
                    "Can you walk me through your current process for {topic}?",
                    "What are the biggest challenges you're facing with {topic}?",
                    "How is your team currently handling {topic}?",
                    "What would success look like for your organization?",
                    "Tell me about your timeline and budget constraints.",
                ]
            else:
                templates = [
                    "We're struggling with {topic}. It's become a real bottleneck.",
                    "Currently we use {solution} but it doesn't scale well.",
                    "We lose about {number} hours a week on manual {topic}.",
                    "The main challenge is {problem}.",
                    "We need something that can handle {requirement}.",
                ]
        elif call_type == "demo":
            if is_company:
                templates = [
                    "Let me show you how this feature works in practice.",
                    "Notice how the UI makes it easy to {action}.",
                    "This is one of the key differentiators compared to {competitor}.",
                    "You can see the real-time monitoring dashboard here.",
                    "Let me demonstrate the integration with {platform}.",
                ]
            else:
                templates = [
                    "How does that compare to what we're using now?",
                    "Can you show me {feature}?",
                    "That's interesting. How would this work with our {system}?",
                    "What's the learning curve like?",
                    "Can we customize that for our specific needs?",
                ]
        else:  # technical or other
            if is_company:
                templates = [
                    "Let me explain the architecture in detail.",
                    "Here's how we handle {technical_aspect}.",
                    "Reliability and uptime are critical. Here's our approach.",
                    "We support {integration} natively.",
                    "Data security is paramount. We use {security_feature}.",
                ]
            else:
                templates = [
                    "How does it handle {technical_concern}?",
                    "What about disaster recovery?",
                    "Can we scale this to {use_case}?",
                    "How does monitoring and alerting work?",
                    "What's your SLA?",
                ]

        template = random.choice(templates)

        # Fill in placeholders
        topics = ["orchestration", "pipelines", "workflows", "data integration", "scheduling"]
        solutions = ["Airflow", "custom scripts", "Dagster", "Prefect"]
        problems = ["brittle retry logic", "manual intervention", "slow deployment", "scaling issues"]
        actions = ["visualize", "configure", "monitor", "debug", "optimize"]
        competitors = ["Airflow", "Dagster", "Oozie", "Luigi"]
        features = ["error handling", "retries", "monitoring", "alerting", "versioning"]
        platforms = ["Kubernetes", "AWS", "Snowflake", "Spark", "dbt"]
        systems = ["Snowflake", "Postgres", "S3", "data warehouse"]
        aspects = ["error handling", "retries", "scalability", "security", "performance"]
        integrations = ["Kubernetes", "Docker", "Git", "Slack", "Email"]
        concerns = ["failover", "data consistency", "security", "audit logging", "compliance"]
        usecases = ["100M+ events/day", "real-time processing", "ML training", "complex dependencies"]
        features_list = ["encryption at rest", "role-based access control", "audit logging", "data residency"]

        return (
            template.replace("{topic}", random.choice(topics))
            .replace("{solution}", random.choice(solutions))
            .replace("{number}", str(random.randint(20, 100)))
            .replace("{problem}", random.choice(problems))
            .replace("{action}", random.choice(actions))
            .replace("{competitor}", random.choice(competitors))
            .replace("{feature}", random.choice(features))
            .replace("{platform}", random.choice(platforms))
            .replace("{system}", random.choice(systems))
            .replace("{technical_aspect}", random.choice(aspects))
            .replace("{integration}", random.choice(integrations))
            .replace("{technical_concern}", random.choice(concerns))
            .replace("{use_case}", random.choice(usecases))
            .replace("{requirement}", random.choice(usecases))
            .replace("{security_feature}", random.choice(features_list))
        )

    # ========================================================================
    # COACHING SESSIONS GENERATION
    # ========================================================================

    def generate_coaching_sessions(self, speakers_for_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate coaching sessions with varied scores."""
        logger.info("Generating coaching sessions...")

        import random

        sessions = []

        for call in self.created_calls:
            # Get Prefect speakers for this call
            call_speakers = [s for s in speakers_for_calls if s["call_id"] == call["id"]]
            company_speakers = [s for s in call_speakers if s["company_side"]]

            # Generate 1-3 coaching sessions per call (for company speakers)
            num_sessions = min(random.randint(1, 3), len(company_speakers))
            reps_to_coach = random.sample(company_speakers, num_sessions)

            for rep in reps_to_coach:
                # Randomly decide if we create a coaching session for this rep
                if random.random() < 0.7:  # 70% chance of having a session
                    dimension = random.choice(COACHING_DIMENSIONS)
                    session_type = random.choice(SESSION_TYPES)

                    # Score based on dimension (some correlations for realism)
                    if dimension == "product_knowledge":
                        score = random.randint(60, 95)
                    elif dimension == "discovery":
                        score = random.randint(50, 90)
                    elif dimension == "objection_handling":
                        score = random.randint(55, 92)
                    else:  # engagement
                        score = random.randint(65, 95)

                    strengths = self._generate_strengths(dimension)
                    improvements = self._generate_improvements(dimension)
                    examples = self._generate_specific_examples(dimension)
                    action_items = self._generate_action_items(dimension, score)

                    session = {
                        "id": str(uuid.uuid4()),
                        "call_id": call["id"],
                        "rep_id": rep["id"],
                        "coaching_dimension": dimension,
                        "session_type": session_type,
                        "analyst": random.choice(["claude-sonnet-4.5", "claude-opus-4.5"]),
                        "created_at": call["scheduled_at"] + timedelta(days=random.randint(1, 5)),
                        "score": score,
                        "strengths": strengths,
                        "areas_for_improvement": improvements,
                        "specific_examples": examples,
                        "action_items": action_items,
                        "full_analysis": self._generate_full_analysis(dimension, score, strengths, improvements),
                    }
                    sessions.append(session)

        logger.info(f"Generated {len(sessions)} coaching sessions")
        self.created_coaching_sessions = sessions
        return sessions

    def _generate_strengths(self, dimension: str) -> list[str]:
        """Generate strength points for a coaching dimension."""
        strengths_map = {
            "product_knowledge": [
                "Accurately explained the product features",
                "Drew clear comparisons to competitors",
                "Positioned the solution for the use case",
                "Explained the technical architecture clearly",
            ],
            "discovery": [
                "Asked open-ended questions",
                "Actively listened and paraphrased",
                "Identified budget constraints early",
                "Probed for pain points effectively",
                "Established clear success criteria",
            ],
            "objection_handling": [
                "Acknowledged the concern respectfully",
                "Provided data-backed responses",
                "Offered alternative solutions",
                "Turned objections into opportunities",
            ],
            "engagement": [
                "Maintained energy throughout the call",
                "Built rapport with the prospect",
                "Kept the prospect engaged",
                "Used relevant examples",
                "Asked for feedback and input",
            ],
        }

        import random

        dimension_strengths = strengths_map.get(dimension, [])
        return random.sample(dimension_strengths, min(random.randint(2, 3), len(dimension_strengths)))

    def _generate_improvements(self, dimension: str) -> list[str]:
        """Generate improvement areas for a coaching dimension."""
        improvements_map = {
            "product_knowledge": [
                "Could have explained the pricing model more clearly",
                "Missed opportunity to mention key features",
                "Could have provided more technical depth",
                "Didn't address scalability concerns",
            ],
            "discovery": [
                "Could have asked more about the decision-making process",
                "Missed probing on timeline",
                "Could have understood the entire buying committee",
                "Didn't fully explore the competing solutions",
            ],
            "objection_handling": [
                "Could have provided more concrete proof points",
                "Missed connecting to similar customer successes",
                "Didn't fully acknowledge the prospect's concern",
                "Could have offered a pilot or trial",
            ],
            "engagement": [
                "Could have asked more questions",
                "Missed some non-verbal cues",
                "Talked too much about the product",
                "Could have been more enthusiastic",
            ],
        }

        import random

        dimension_improvements = improvements_map.get(dimension, [])
        return random.sample(dimension_improvements, min(random.randint(1, 2), len(dimension_improvements)))

    def _generate_specific_examples(self, dimension: str) -> dict[str, Any]:
        """Generate specific transcript examples for coaching."""
        examples = {
            "good": [
                {
                    "quote": "Can you help me understand your current process for managing workflows?",
                    "timestamp": 120,
                    "analysis": "Strong open-ended question that invites the prospect to share details.",
                },
                {
                    "quote": "I see. So the main challenge is that manual retries slow down your deployments.",
                    "timestamp": 240,
                    "analysis": "Excellent paraphrasing that shows active listening.",
                },
            ],
            "needs_work": [
                {
                    "quote": "Our product is the best in the market.",
                    "timestamp": 480,
                    "analysis": "Too broad; should support with specific features or evidence.",
                },
            ],
        }
        return examples

    def _generate_action_items(self, dimension: str, score: int) -> list[str]:
        """Generate action items based on score and dimension."""
        import random

        base_items = [
            "Review product knowledge documentation",
            "Practice discovery questions",
            "Study competitor positioning",
            "Record and review a call",
            "Attend skills training",
            "Work with a mentor on this dimension",
            "Practice objection handling scenarios",
        ]

        # Higher scores = fewer action items
        num_items = max(1, 3 - (score // 33))
        return random.sample(base_items, num_items)

    def _generate_full_analysis(self, dimension: str, score: int, strengths: list[str], improvements: list[str]) -> str:
        """Generate a full analysis narrative."""
        rating = "excellent" if score >= 85 else "good" if score >= 70 else "needs improvement"

        analysis = f"Overall {rating} performance on {dimension.replace('_', ' ')}. "
        analysis += f"The rep demonstrated {len(strengths)} key strengths: {', '.join(strengths[:2]).lower()}. "
        analysis += f"Focus areas for continued development include: {', '.join(improvements[:2]).lower()}. "
        analysis += "Recommend focused practice on identified areas and reviewing past call recordings."

        return analysis

    # ========================================================================
    # CALL-OPPORTUNITY LINKING
    # ========================================================================

    def generate_call_opportunities(self) -> list[dict[str, Any]]:
        """Link calls to opportunities."""
        logger.info("Linking calls to opportunities...")

        import random

        call_opps = []
        calls_per_opp = max(1, self.num_calls // len(self.created_opportunities))

        for opp in self.created_opportunities:
            # Assign 1-3 calls to each opportunity
            num_calls = random.randint(1, 3)
            assigned_calls = random.sample(self.created_calls, min(num_calls, len(self.created_calls)))

            for call in assigned_calls:
                call_opps.append({
                    "call_id": call["id"],
                    "opportunity_id": opp["id"],
                })

        logger.info(f"Generated {len(call_opps)} call-opportunity links")
        return call_opps

    # ========================================================================
    # EMAIL GENERATION
    # ========================================================================

    def generate_emails(self) -> list[dict[str, Any]]:
        """Generate sample emails for opportunities."""
        logger.info("Generating emails...")

        import random

        emails = []
        email_templates = [
            {
                "subject_template": "Re: {opportunity_name} - Next Steps",
                "body_template": "Hi {prospect_name}, Following up on our call. I wanted to share some resources about how Prefect handles {pain_point}...",
            },
            {
                "subject_template": "{opportunity_name} - Technical Proposal",
                "body_template": "Hi {prospect_name}, Attached is the technical proposal we discussed. This outlines how Prefect integrates with {tech_stack}...",
            },
            {
                "subject_template": "Re: Implementation Timeline for {opportunity_name}",
                "body_template": "Hi {prospect_name}, Based on our discussion, here's a proposed implementation timeline. We can start the POC {timeline}...",
            },
            {
                "subject_template": "{opportunity_name} - Pricing and Terms",
                "body_template": "Hi {prospect_name}, Per our conversation, here's the detailed pricing breakdown. Given your timeline, we recommend {recommendation}...",
            },
        ]

        ae_speakers = [s for s in self.created_speakers if s["role"] == "ae"]

        for opp in self.created_opportunities:
            # Generate 2-5 emails per opportunity
            num_emails = random.randint(2, 5)

            for i in range(num_emails):
                template = random.choice(email_templates)
                ae = random.choice(ae_speakers)

                prospect_name = "there"  # Generic fallback
                subject = (
                    template["subject_template"]
                    .replace("{opportunity_name}", opp["name"])
                    .replace("{pain_point}", random.choice(PAIN_POINTS))
                )

                body = (
                    template["body_template"]
                    .replace("{prospect_name}", prospect_name)
                    .replace("{pain_point}", random.choice(PAIN_POINTS))
                    .replace("{tech_stack}", random.choice(TECH_STACKS))
                    .replace("{timeline}", random.choice(["in two weeks", "next month", "in three weeks"]))
                    .replace("{recommendation}", random.choice(["starting with a 4-week POC", "a phased rollout", "an MVP first"]))
                )

                email = {
                    "id": str(uuid.uuid4()),
                    "gong_email_id": f"gong-email-{len(emails):04d}",
                    "opportunity_id": opp["id"],
                    "subject": subject,
                    "sender_email": ae["email"],
                    "recipients": [f"{random.choice(FIRST_NAMES).lower()}@{opp['account_name'].replace(' ', '').lower()}.com"],
                    "sent_at": opp["created_at"] + timedelta(days=random.randint(1, 30)),
                    "body_snippet": body[:200] + "...",
                    "metadata": {
                        "thread_id": f"thread-{len(emails):04d}",
                        "has_attachment": random.choice([True, False, False]),  # 33% have attachments
                    },
                }
                emails.append(email)

        logger.info(f"Generated {len(emails)} emails")
        self.created_emails = emails
        return emails

    # ========================================================================
    # DATABASE INSERTION
    # ========================================================================

    def insert_all_data(self) -> dict[str, int]:
        """Insert all generated data into the database."""
        logger.info("Inserting all data into database...")

        counts = {
            "speakers": 0,
            "calls": 0,
            "call_speakers": 0,
            "transcripts": 0,
            "opportunities": 0,
            "call_opportunities": 0,
            "coaching_sessions": 0,
            "emails": 0,
        }

        try:
            # Insert speakers (Prefect employees)
            speaker_params = [
                (
                    s["id"],
                    s["name"],
                    s["email"],
                    s["role"],
                    s["company_side"],
                )
                for s in self.created_speakers
            ]
            if speaker_params:
                execute_many(
                    """
                    INSERT INTO speakers (id, name, email, role, company_side)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    speaker_params,
                )
                counts["speakers"] = len(speaker_params)

            # Insert calls
            call_params = [
                (
                    c["id"],
                    c["gong_call_id"],
                    c["title"],
                    c["scheduled_at"],
                    c["duration_seconds"],
                    c["call_type"],
                    c["product"],
                    c["created_at"],
                    c["processed_at"],
                    str(c["metadata"]),
                )
                for c in self.created_calls
            ]
            if call_params:
                execute_many(
                    """
                    INSERT INTO calls (id, gong_call_id, title, scheduled_at, duration_seconds,
                                      call_type, product, created_at, processed_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (gong_call_id) DO NOTHING
                    """,
                    call_params,
                )
                counts["calls"] = len(call_params)

            # Insert call speakers
            call_speaker_params = []
            for call in self.created_calls:
                call_speakers = [s for s in self._all_speakers_for_calls if s["call_id"] == call["id"]]
                for s in call_speakers:
                    call_speaker_params.append(
                        (
                            s["id"],
                            s["call_id"],
                            s["name"],
                            s["email"],
                            s["role"],
                            s["company_side"],
                            s["talk_time_seconds"],
                            s["talk_time_percentage"],
                        )
                    )

            if call_speaker_params:
                execute_many(
                    """
                    INSERT INTO speakers (id, call_id, name, email, role, company_side,
                                         talk_time_seconds, talk_time_percentage)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    call_speaker_params,
                )
                counts["call_speakers"] = len(call_speaker_params)

            # Insert transcripts
            if self._all_transcripts:
                transcript_params = [
                    (
                        t["id"],
                        t["call_id"],
                        t["speaker_id"],
                        t["sequence_number"],
                        t["timestamp_seconds"],
                        t["text"],
                        t["sentiment"],
                        str(t["topics"]),
                    )
                    for t in self._all_transcripts
                ]
                execute_many(
                    """
                    INSERT INTO transcripts (id, call_id, speaker_id, sequence_number,
                                           timestamp_seconds, text, sentiment, topics)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::varchar[])
                    ON CONFLICT (id) DO NOTHING
                    """,
                    transcript_params,
                )
                counts["transcripts"] = len(transcript_params)

            # Insert opportunities
            opp_params = [
                (
                    o["id"],
                    o["gong_opportunity_id"],
                    o["name"],
                    o["account_name"],
                    o["owner_email"],
                    o["stage"],
                    o["close_date"],
                    o["amount"],
                    o["health_score"],
                    str(o["metadata"]),
                )
                for o in self.created_opportunities
            ]
            if opp_params:
                execute_many(
                    """
                    INSERT INTO opportunities (id, gong_opportunity_id, name, account_name,
                                              owner_email, stage, close_date, amount,
                                              health_score, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (gong_opportunity_id) DO NOTHING
                    """,
                    opp_params,
                )
                counts["opportunities"] = len(opp_params)

            # Insert call-opportunity links
            call_opp_params = [
                (c["call_id"], c["opportunity_id"])
                for c in self._all_call_opps
            ]
            if call_opp_params:
                execute_many(
                    """
                    INSERT INTO call_opportunities (call_id, opportunity_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    call_opp_params,
                )
                counts["call_opportunities"] = len(call_opp_params)

            # Insert coaching sessions
            if self._all_coaching_sessions:
                coaching_params = [
                    (
                        c["id"],
                        c["call_id"],
                        c["rep_id"],
                        c["coaching_dimension"],
                        c["session_type"],
                        c["analyst"],
                        c["created_at"],
                        c["score"],
                        str(c["strengths"]),
                        str(c["areas_for_improvement"]),
                        str(c["specific_examples"]),
                        str(c["action_items"]),
                        c["full_analysis"],
                    )
                    for c in self._all_coaching_sessions
                ]
                execute_many(
                    """
                    INSERT INTO coaching_sessions (id, call_id, rep_id, coaching_dimension,
                                                  session_type, analyst, created_at, score,
                                                  strengths, areas_for_improvement,
                                                  specific_examples, action_items, full_analysis)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::text[], %s::text[],
                            %s::jsonb, %s::text[], %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    coaching_params,
                )
                counts["coaching_sessions"] = len(coaching_params)

            # Insert emails
            if self._all_emails:
                email_params = [
                    (
                        e["id"],
                        e["gong_email_id"],
                        e["opportunity_id"],
                        e["subject"],
                        e["sender_email"],
                        str(e["recipients"]),
                        e["sent_at"],
                        e["body_snippet"],
                        str(e["metadata"]),
                    )
                    for e in self._all_emails
                ]
                execute_many(
                    """
                    INSERT INTO emails (id, gong_email_id, opportunity_id, subject,
                                       sender_email, recipients, sent_at, body_snippet, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s::text[], %s, %s, %s::jsonb)
                    ON CONFLICT (gong_email_id) DO NOTHING
                    """,
                    email_params,
                )
                counts["emails"] = len(email_params)

            logger.info("All data inserted successfully")

        except Exception as e:
            logger.error(f"Error inserting data: {e}", exc_info=True)
            raise

        return counts

    def generate_all(self) -> dict[str, int]:
        """Generate all fixtures and insert into database."""
        logger.info("="*80)
        logger.info("Starting fixtures generation")
        logger.info("="*80)
        logger.info(f"Configuration: {self.num_calls} calls, {self.days_back} days lookback")
        logger.info("")

        # Generate all data
        self.generate_speakers()
        self.generate_opportunities()
        self.generate_calls()
        self._all_speakers_for_calls = self.generate_call_speakers()
        self._all_transcripts = self.generate_transcripts(self._all_speakers_for_calls)
        self._all_coaching_sessions = self.generate_coaching_sessions(self._all_speakers_for_calls)
        self._all_call_opps = self.generate_call_opportunities()
        self._all_emails = self.generate_emails()

        # Insert into database
        counts = self.insert_all_data()

        logger.info("")
        logger.info("="*80)
        logger.info("Fixtures generation complete!")
        logger.info("="*80)
        logger.info(f"Created:")
        logger.info(f"  - {counts['speakers']} Prefect employees (speakers)")
        logger.info(f"  - {counts['calls']} calls")
        logger.info(f"  - {counts['call_speakers']} call participants")
        logger.info(f"  - {counts['transcripts']} transcript lines")
        logger.info(f"  - {counts['opportunities']} opportunities")
        logger.info(f"  - {counts['call_opportunities']} call-opportunity links")
        logger.info(f"  - {counts['coaching_sessions']} coaching sessions")
        logger.info(f"  - {counts['emails']} emails")
        logger.info("")

        # Show summary statistics
        self._show_summary_stats()

        return counts

    def _show_summary_stats(self) -> None:
        """Display summary statistics about generated data."""
        try:
            # Calls by type
            call_types = fetch_all("""
                SELECT call_type, COUNT(*) as count
                FROM calls
                WHERE created_at > NOW() - INTERVAL '1 day'
                GROUP BY call_type
                ORDER BY count DESC
            """)
            if call_types:
                logger.info("Calls by type:")
                for row in call_types:
                    logger.info(f"  - {row.get('call_type', 'unknown')}: {row['count']}")

            # Coaching sessions by dimension
            dimensions = fetch_all("""
                SELECT coaching_dimension, COUNT(*) as count, AVG(score) as avg_score
                FROM coaching_sessions
                WHERE created_at > NOW() - INTERVAL '1 day'
                GROUP BY coaching_dimension
                ORDER BY count DESC
            """)
            if dimensions:
                logger.info("Coaching sessions by dimension:")
                for row in dimensions:
                    logger.info(
                        f"  - {row.get('coaching_dimension', 'unknown')}: "
                        f"{row['count']} sessions (avg score: {row.get('avg_score', 0):.1f})"
                    )

            # Opportunities by stage
            stages = fetch_all("""
                SELECT stage, COUNT(*) as count
                FROM opportunities
                WHERE created_at > NOW() - INTERVAL '1 day'
                GROUP BY stage
                ORDER BY count DESC
            """)
            if stages:
                logger.info("Opportunities by stage:")
                for row in stages:
                    logger.info(f"  - {row.get('stage', 'unknown')}: {row['count']}")

        except Exception as e:
            logger.warning(f"Could not retrieve summary stats: {e}")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main entry point for fixtures generation."""
    parser = argparse.ArgumentParser(
        description="Generate realistic sample data and fixtures for call coaching application"
    )
    parser.add_argument(
        "--num-calls",
        type=int,
        default=20,
        help="Number of sample calls to generate (default: 20)",
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=90,
        help="Generate calls from the last N days (default: 90)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: none)",
    )
    parser.add_argument(
        "--demo-account",
        action="store_true",
        help="Set up a demo account with realistic data for stakeholder demos",
    )

    args = parser.parse_args()

    # Ensure logs directory exists
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    try:
        # Adjust parameters for demo account
        if args.demo_account:
            logger.info("Setting up demo account with realistic data...")
            num_calls = 50  # More calls for demo
            days_back = 180  # 6 months of history
        else:
            num_calls = args.num_calls
            days_back = args.days_back

        generator = FixturesGenerator(
            num_calls=num_calls,
            days_back=days_back,
            seed=args.seed,
        )

        counts = generator.generate_all()

        # Exit with success
        logger.info("Fixtures generation successful!")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\nFixtures generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fixtures generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
