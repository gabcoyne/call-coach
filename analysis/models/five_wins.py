"""
Pydantic models for Five Wins Coaching Framework.

These models define the data structures for evaluating calls against the Five Wins
framework and generating coaching output.

Key design principles:
1. JSON serializable for API responses
2. Validated scores and status values
3. Clear hierarchy: WinProgress -> FiveWinsEvaluation -> CoachingOutput
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

WinName = Literal["business", "technical", "security", "commercial", "legal"]
WinStatus = Literal["met", "partial", "missed"]
BusinessCaseStrength = Literal["weak", "moderate", "strong"]


class WinProgress(BaseModel):
    """Base model for progress toward securing a single win."""

    score: int = Field(ge=0, le=100, description="Score 0-100 for this win")
    exit_criteria_met: bool = Field(
        default=False, description="Whether the exit criteria has been satisfied"
    )
    discovery_complete: bool = Field(
        default=False, description="Whether necessary discovery has been completed"
    )
    blockers: list[str] = Field(
        default_factory=list, description="What's preventing progress on this win"
    )
    evidence: list[str] = Field(
        default_factory=list, description="Quotes/moments supporting the score"
    )

    @property
    def status(self) -> WinStatus:
        """Derive status from score."""
        if self.exit_criteria_met or self.score >= 90:
            return "met"
        elif self.score >= 50:
            return "partial"
        return "missed"


class ChampionAssessment(BaseModel):
    """Business Win specific: Champion evaluation using the 3 I's."""

    identified: bool = Field(default=False, description="Is there an identified champion?")
    name: str | None = Field(default=None, description="Name of the champion if known")
    incentive_clear: bool = Field(default=False, description="What's in it for them personally?")
    influence_confirmed: bool = Field(
        default=False, description="Can they actually move the deal forward?"
    )
    information_flowing: bool = Field(
        default=False, description="Are they giving real intel about the org?"
    )

    @property
    def strength(self) -> int:
        """Calculate champion strength as number of I's confirmed (0-3)."""
        return sum([self.incentive_clear, self.influence_confirmed, self.information_flowing])


class BusinessWinEvaluation(WinProgress):
    """Extended evaluation for Business Win (35 points max)."""

    champion: ChampionAssessment | None = Field(
        default=None, description="Champion assessment using the 3 I's"
    )
    budget_confirmed: bool = Field(default=False, description="Has budget been confirmed?")
    exec_sponsor_engaged: bool = Field(
        default=False, description="Is an executive sponsor engaged?"
    )
    business_case_strength: BusinessCaseStrength = Field(
        default="weak", description="Strength of the business case"
    )

    @field_validator("score")
    @classmethod
    def validate_business_score(cls, v: int) -> int:
        """Business Win max score is 35."""
        if v > 35:
            raise ValueError("Business Win score cannot exceed 35")
        return v


class TechnicalWinEvaluation(WinProgress):
    """Extended evaluation for Technical Win (25 points max)."""

    vendor_of_choice_confirmed: bool = Field(
        default=False, description="Have they said Prefect is their vendor of choice?"
    )
    poc_scoped: bool = Field(default=False, description="Is a POC properly scoped?")
    poc_success_criteria_defined: bool = Field(
        default=False, description="Are POC success criteria defined?"
    )

    @field_validator("score")
    @classmethod
    def validate_technical_score(cls, v: int) -> int:
        """Technical Win max score is 25."""
        if v > 25:
            raise ValueError("Technical Win score cannot exceed 25")
        return v


class SecurityWinEvaluation(WinProgress):
    """Extended evaluation for Security Win (15 points max)."""

    infosec_timeline_known: bool = Field(
        default=False, description="Is the InfoSec review timeline known?"
    )
    trust_portal_shared: bool = Field(
        default=False, description="Has the trust portal been shared?"
    )
    architecture_review_scheduled: bool = Field(
        default=False, description="Is an architecture review scheduled?"
    )

    @field_validator("score")
    @classmethod
    def validate_security_score(cls, v: int) -> int:
        """Security Win max score is 15."""
        if v > 15:
            raise ValueError("Security Win score cannot exceed 15")
        return v


class CommercialWinEvaluation(WinProgress):
    """Extended evaluation for Commercial Win (15 points max)."""

    exec_sponsor_aligned: bool = Field(
        default=False, description="Is the exec sponsor aligned on commercials?"
    )
    scope_agreed: bool = Field(default=False, description="Is deployment scope agreed?")
    pricing_discussed: bool = Field(default=False, description="Has pricing been discussed?")

    @field_validator("score")
    @classmethod
    def validate_commercial_score(cls, v: int) -> int:
        """Commercial Win max score is 15."""
        if v > 15:
            raise ValueError("Commercial Win score cannot exceed 15")
        return v


class LegalWinEvaluation(WinProgress):
    """Extended evaluation for Legal Win (10 points max)."""

    terms_impact_discussed: bool = Field(
        default=False, description="Were price-impacting terms discussed early?"
    )
    legal_timeline_known: bool = Field(
        default=False, description="Is the legal review timeline known?"
    )
    redlines_in_progress: bool = Field(
        default=False, description="Are contract redlines in progress?"
    )

    @field_validator("score")
    @classmethod
    def validate_legal_score(cls, v: int) -> int:
        """Legal Win max score is 10."""
        if v > 10:
            raise ValueError("Legal Win score cannot exceed 10")
        return v


class FiveWinsEvaluation(BaseModel):
    """Complete Five Wins evaluation for a call."""

    business: BusinessWinEvaluation = Field(description="Business Win evaluation")
    technical: TechnicalWinEvaluation = Field(description="Technical Win evaluation")
    security: SecurityWinEvaluation = Field(description="Security Win evaluation")
    commercial: CommercialWinEvaluation = Field(description="Commercial Win evaluation")
    legal: LegalWinEvaluation = Field(description="Legal Win evaluation")

    @property
    def overall_score(self) -> int:
        """Calculate overall score as sum of individual win scores."""
        return (
            self.business.score
            + self.technical.score
            + self.security.score
            + self.commercial.score
            + self.legal.score
        )

    @property
    def wins_secured(self) -> int:
        """Count wins where exit criteria is met."""
        return sum(
            1
            for win in [
                self.business,
                self.technical,
                self.security,
                self.commercial,
                self.legal,
            ]
            if win.exit_criteria_met
        )

    @property
    def at_risk_wins(self) -> list[str]:
        """List wins that are at risk (score < 50, not met)."""
        wins = []
        for name, win in [
            ("business", self.business),
            ("technical", self.technical),
            ("security", self.security),
            ("commercial", self.commercial),
            ("legal", self.legal),
        ]:
            if win.score < 50 and not win.exit_criteria_met:
                wins.append(name)
        return wins

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to include computed properties."""
        data: dict[str, Any] = super().model_dump(**kwargs)
        data["overall_score"] = self.overall_score
        data["wins_secured"] = self.wins_secured
        data["at_risk_wins"] = self.at_risk_wins
        return data


class CallMoment(BaseModel):
    """A specific moment in the call to reference in coaching."""

    timestamp_seconds: int = Field(ge=0, description="Timestamp in seconds from call start")
    speaker: str = Field(description="Who was speaking at this moment")
    summary: str = Field(description="Brief summary of what happened at this moment")


class PrimaryAction(BaseModel):
    """The ONE thing the rep should do before their next call."""

    win: WinName = Field(description="Which win this action relates to")
    action: str = Field(description="Specific, actionable instruction (what exactly to do/say)")
    context: str = Field(description="Why this matters, linked to what happened in the call")
    related_moment: CallMoment | None = Field(
        default=None, description="The call moment that makes this action important"
    )


class CoachingOutput(BaseModel):
    """Final coaching output - what the rep sees.

    This is the primary output format for call coaching, designed to be:
    - Concise: 2-3 sentence narrative
    - Actionable: ONE specific thing to do
    - Connected: Tied to specific call moments
    - Jargon-free: No methodology names (SPICED, Challenger, etc.)
    """

    # Primary: 2-3 sentence narrative
    narrative: str = Field(description="2-3 sentence summary of call performance and key insight")

    # Win progress summary
    wins_addressed: dict[str, str] = Field(
        default_factory=dict,
        description="Map of win name to what was accomplished",
    )
    wins_missed: dict[str, str] = Field(
        default_factory=dict,
        description="Map of win name to what was missed/needs work",
    )

    # Single action item - the most important thing
    primary_action: PrimaryAction = Field(description="The ONE most important action for the rep")

    # Supporting detail (collapsed by default in UI)
    five_wins_detail: FiveWinsEvaluation = Field(
        description="Full Five Wins evaluation with all scores"
    )
    key_moments: list[CallMoment] = Field(
        default_factory=list,
        description="Top moments from the call worth reviewing",
    )
