/**
 * Rubric Evaluation Types
 *
 * TypeScript interfaces for Five Wins framework and supplementary coaching frameworks.
 * These types align with the backend's Five Wins evaluation structure.
 */

/**
 * Exchange Evidence - New evidence format using exchange_summary
 *
 * Replaces isolated quote snippets with contextualized exchanges that show
 * the back-and-forth conversation and its impact on the win/criterion.
 */
export interface ExchangeEvidence {
  /** Start time of the exchange in seconds from call start */
  timestamp_start: number;

  /** End time of the exchange in seconds from call start */
  timestamp_end: number;

  /**
   * Summary of the exchange (what was said by both parties)
   * Example: "When prospect raised pricing concerns, rep reframed around ROI
   * and asked discovery questions about current costs and pain points."
   */
  exchange_summary: string;

  /**
   * Why this exchange matters for this win/criterion
   * Example: "Demonstrated value selling skills and kept control rather than
   * getting defensive. Moved conversation from price to value."
   */
  impact: string;
}

/**
 * Win Evaluation - Individual win assessment
 *
 * Represents evaluation of a single win from the Five Wins framework
 * (Business, Technical, Security, Commercial, Legal).
 */
export interface WinEvaluation {
  /** Score achieved for this win (0 to max_score) */
  score: number;

  /** Maximum possible score for this win */
  max_score: number;

  /**
   * Win status
   * - "met": Achieved threshold (typically 70%+ of max_score)
   * - "partial": Some progress but below threshold
   * - "missed": Little to no evidence of addressing this win
   */
  status: "met" | "partial" | "missed";

  /**
   * Exchange evidence showing how this win was addressed (or missed)
   * Contains up to 5 key exchanges with timestamp ranges and impact statements
   */
  evidence: ExchangeEvidence[];
}

/**
 * Five Wins Evaluation - Complete Five Wins framework assessment
 *
 * Aggregated evaluation across all five wins (Business, Technical, Security, Commercial, Legal).
 * This is the primary coaching framework returned by the analyze_call API.
 */
export interface FiveWinsEvaluation {
  /**
   * Business Win (35 points max)
   * - Identified business pain/problem
   * - Quantified impact of solving it
   * - Connected to strategic initiatives
   */
  business_win: WinEvaluation;

  /**
   * Technical Win (25 points max)
   * - Technical requirements understood
   * - Solution fit validated
   * - Technical champion identified
   */
  technical_win: WinEvaluation;

  /**
   * Security Win (15 points max)
   * - Security requirements captured
   * - Compliance needs understood
   * - Security/IT stakeholder engaged
   */
  security_win: WinEvaluation;

  /**
   * Commercial Win (15 points max)
   * - Budget/pricing discussed
   * - Procurement process understood
   * - Economic buyer identified
   */
  commercial_win: WinEvaluation;

  /**
   * Legal Win (10 points max)
   * - Legal requirements captured
   * - Contract/MSA needs understood
   * - Legal stakeholder engaged
   */
  legal_win: WinEvaluation;

  /**
   * Count of wins that met threshold (status = "met")
   * Range: 0-5
   */
  wins_secured: number;

  /**
   * Overall score summing all five wins
   * Range: 0-100
   */
  overall_score: number;
}

/**
 * Criterion Evaluation - Assessment of a single criterion in a supplementary framework
 *
 * Used for SPICED (Situation, Pain, Impact, Critical Event, Decision),
 * Challenger (Teaching, Tailoring, Taking Control),
 * and Sandler (Pain-Budget-Decision) frameworks.
 */
export interface CriterionEvaluation {
  /**
   * Criterion name (e.g., "situation", "pain", "teaching", "budget")
   * snake_case format
   */
  criterion: string;

  /**
   * Score for this criterion (0 to max_score)
   * Typically 20 points per criterion in SPICED
   */
  score: number;

  /** Maximum possible score for this criterion */
  max_score: number;

  /**
   * Status of this criterion
   * - "met": Strong execution (typically 70%+ of max_score)
   * - "partial": Some evidence but incomplete
   * - "missed": Little to no evidence
   */
  status: "met" | "partial" | "missed";

  /**
   * Exchange evidence showing how this criterion was addressed
   * Up to 3 key exchanges per criterion
   */
  evidence: ExchangeEvidence[];

  /**
   * Optional explanation for why this was missed or needs work
   * Particularly useful for "partial" or "missed" status
   */
  missed_explanation?: string;
}

/**
 * Supplementary Frameworks - Additional coaching frameworks beyond Five Wins
 *
 * These frameworks (SPICED, Challenger, Sandler) provide deeper insights into
 * specific coaching dimensions like discovery, engagement, and objection handling.
 * They are displayed in a collapsed panel below the primary Five Wins scorecard.
 */
export interface SupplementaryFrameworks {
  /**
   * Discovery Rubric - SPICED framework evaluation
   * Situation, Pain, Impact, Critical Event, Decision
   */
  discovery_rubric?: {
    overall_score: number;
    max_score: number;
    criteria: CriterionEvaluation[];
  };

  /**
   * Engagement Rubric - Challenger methodology evaluation
   * Teaching, Tailoring, Taking Control
   */
  engagement_rubric?: {
    overall_score: number;
    max_score: number;
    criteria: CriterionEvaluation[];
  };

  /**
   * Objection Handling Rubric - Sandler methodology evaluation
   * Pain-Budget-Decision qualification
   */
  objection_handling_rubric?: {
    overall_score: number;
    max_score: number;
    criteria: CriterionEvaluation[];
  };

  /**
   * Product Knowledge Rubric - Technical depth evaluation
   * Feature knowledge, use case alignment, competitive positioning
   */
  product_knowledge_rubric?: {
    overall_score: number;
    max_score: number;
    criteria: CriterionEvaluation[];
  };
}
