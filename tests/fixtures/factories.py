"""
Test data factories for generating realistic test data.

Uses Faker to generate consistent, realistic test data for all entities.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from faker import Faker

fake = Faker()


class CallFactory:
    """Factory for generating call data."""

    @staticmethod
    def create(
        call_id: str | None = None,
        rep_id: str | None = None,
        opportunity_id: str | None = None,
        duration: int | None = None,
        call_date: datetime | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create a call record with realistic data."""
        return {
            "id": call_id or str(uuid4()),
            "rep_id": rep_id or str(uuid4()),
            "opportunity_id": opportunity_id or str(uuid4()),
            "duration": duration or fake.random_int(min=300, max=3600),
            "call_date": call_date or fake.date_time_between(start_date="-30d", end_date="now"),
            "transcript": fake.text(max_nb_chars=2000),
            "recording_url": fake.url(),
            "title": fake.catch_phrase(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple call records."""
        return [CallFactory.create(**kwargs) for _ in range(count)]


class RepFactory:
    """Factory for generating rep (sales representative) data."""

    @staticmethod
    def create(
        rep_id: str | None = None,
        email: str | None = None,
        name: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create a rep record with realistic data."""
        return {
            "id": rep_id or str(uuid4()),
            "email": email or fake.email(),
            "name": name or fake.name(),
            "role": fake.random_element(elements=["SDR", "AE", "CSM", "Manager"]),
            "team": fake.random_element(elements=["Enterprise", "SMB", "Mid-Market"]),
            "hire_date": fake.date_between(start_date="-2y", end_date="today"),
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple rep records."""
        return [RepFactory.create(**kwargs) for _ in range(count)]


class OpportunityFactory:
    """Factory for generating opportunity data."""

    @staticmethod
    def create(
        opportunity_id: str | None = None,
        rep_id: str | None = None,
        amount: float | None = None,
        stage: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create an opportunity record with realistic data."""
        stages = [
            "Discovery",
            "Qualification",
            "Proposal",
            "Negotiation",
            "Closed Won",
            "Closed Lost",
        ]

        return {
            "id": opportunity_id or str(uuid4()),
            "rep_id": rep_id or str(uuid4()),
            "company_name": fake.company(),
            "amount": amount or float(fake.random_int(min=10000, max=500000)),
            "stage": stage or fake.random_element(elements=stages),
            "close_date": fake.date_between(start_date="today", end_date="+90d"),
            "created_date": fake.date_between(start_date="-60d", end_date="today"),
            "probability": fake.random_int(min=0, max=100),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple opportunity records."""
        return [OpportunityFactory.create(**kwargs) for _ in range(count)]


class AnalysisFactory:
    """Factory for generating analysis data."""

    @staticmethod
    def create(
        analysis_id: str | None = None,
        call_id: str | None = None,
        dimension: str | None = None,
        score: float | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create an analysis record with realistic data."""
        dimensions = [
            "discovery_quality",
            "objection_handling",
            "product_knowledge",
            "closing_technique",
            "rapport_building",
        ]

        return {
            "id": analysis_id or str(uuid4()),
            "call_id": call_id or str(uuid4()),
            "dimension": dimension or fake.random_element(elements=dimensions),
            "score": score if score is not None else round(fake.random.uniform(0.0, 10.0), 2),
            "feedback": fake.paragraph(nb_sentences=3),
            "strengths": [fake.sentence() for _ in range(2)],
            "areas_for_improvement": [fake.sentence() for _ in range(2)],
            "specific_examples": [fake.sentence() for _ in range(2)],
            "analyzed_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple analysis records."""
        return [AnalysisFactory.create(**kwargs) for _ in range(count)]


class CoachingSessionFactory:
    """Factory for generating coaching session data."""

    @staticmethod
    def create(
        session_id: str | None = None,
        rep_id: str | None = None,
        coach_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create a coaching session record with realistic data."""
        return {
            "id": session_id or str(uuid4()),
            "rep_id": rep_id or str(uuid4()),
            "coach_id": coach_id or str(uuid4()),
            "session_date": fake.date_time_between(start_date="-30d", end_date="now"),
            "duration": fake.random_int(min=1800, max=3600),
            "topics": [fake.word() for _ in range(3)],
            "goals": [fake.sentence() for _ in range(2)],
            "action_items": [fake.sentence() for _ in range(3)],
            "notes": fake.paragraph(nb_sentences=5),
            "follow_up_date": fake.date_between(start_date="today", end_date="+14d"),
            "status": fake.random_element(elements=["scheduled", "completed", "cancelled"]),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple coaching session records."""
        return [CoachingSessionFactory.create(**kwargs) for _ in range(count)]


class InsightFactory:
    """Factory for generating insight data."""

    @staticmethod
    def create(
        insight_id: str | None = None,
        rep_id: str | None = None,
        insight_type: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create an insight record with realistic data."""
        insight_types = ["trend", "achievement", "area_of_concern", "recommendation"]

        return {
            "id": insight_id or str(uuid4()),
            "rep_id": rep_id or str(uuid4()),
            "insight_type": insight_type or fake.random_element(elements=insight_types),
            "title": fake.catch_phrase(),
            "description": fake.paragraph(nb_sentences=3),
            "metric_name": fake.word(),
            "metric_value": round(fake.random.uniform(0.0, 100.0), 2),
            "trend_direction": fake.random_element(elements=["up", "down", "stable"]),
            "priority": fake.random_element(elements=["high", "medium", "low"]),
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),
            **kwargs,
        }

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[dict[str, Any]]:
        """Create multiple insight records."""
        return [InsightFactory.create(**kwargs) for _ in range(count)]


# Convenience function to create related test data
def create_test_scenario(
    num_reps: int = 2, calls_per_rep: int = 3, opportunities_per_rep: int = 2
) -> dict[str, list[dict[str, Any]]]:
    """
    Create a complete test scenario with related data.

    Returns:
        Dictionary with keys: reps, calls, opportunities, analyses
    """
    reps = RepFactory.create_batch(num_reps)
    calls = []
    opportunities = []
    analyses = []

    for rep in reps:
        # Create opportunities for this rep
        rep_opportunities = OpportunityFactory.create_batch(opportunities_per_rep, rep_id=rep["id"])
        opportunities.extend(rep_opportunities)

        # Create calls for this rep
        for opp in rep_opportunities[:calls_per_rep]:
            call = CallFactory.create(rep_id=rep["id"], opportunity_id=opp["id"])
            calls.append(call)

            # Create analysis for this call
            analysis = AnalysisFactory.create(call_id=call["id"])
            analyses.append(analysis)

    return {
        "reps": reps,
        "calls": calls,
        "opportunities": opportunities,
        "analyses": analyses,
    }
