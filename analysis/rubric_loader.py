"""
Rubric loading and validation module for role-based coaching.

Loads role-specific coaching rubrics (AE, SE, CSM) from JSON files,
validates their structure, and provides cached access for analysis.
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# In-memory cache for loaded rubrics
_rubric_cache: dict[str, dict[str, Any]] = {}

# Path to rubrics directory
RUBRICS_DIR = Path(__file__).parent / "rubrics"


class RubricValidationError(Exception):
    """Raised when rubric validation fails."""
    pass


def validate_rubric(rubric_dict: dict[str, Any]) -> None:
    """
    Validate rubric structure and content.

    Args:
        rubric_dict: Parsed rubric JSON

    Raises:
        RubricValidationError: If validation fails
    """
    # Check required top-level fields
    required_fields = ["role", "role_name", "dimensions"]
    missing_fields = [f for f in required_fields if f not in rubric_dict]
    if missing_fields:
        raise RubricValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

    # Validate dimensions array
    dimensions = rubric_dict["dimensions"]
    if not isinstance(dimensions, list) or len(dimensions) == 0:
        raise RubricValidationError("dimensions must be a non-empty array")

    # Validate each dimension
    dimension_fields = ["id", "name", "weight", "criteria", "scoring"]
    scoring_bands = ["0-49", "50-69", "70-89", "90-100"]

    total_weight = 0.0
    for i, dim in enumerate(dimensions):
        # Check dimension fields
        missing = [f for f in dimension_fields if f not in dim]
        if missing:
            raise RubricValidationError(
                f"Dimension {i} ({dim.get('id', 'unknown')}) missing fields: {', '.join(missing)}"
            )

        # Validate weight is numeric
        try:
            weight = float(dim["weight"])
            total_weight += weight
        except (ValueError, TypeError):
            raise RubricValidationError(
                f"Dimension {dim['id']}: weight must be numeric, got {dim['weight']}"
            )

        # Validate criteria is array
        if not isinstance(dim["criteria"], list) or len(dim["criteria"]) == 0:
            raise RubricValidationError(
                f"Dimension {dim['id']}: criteria must be non-empty array"
            )

        # Validate scoring bands
        if not isinstance(dim["scoring"], dict):
            raise RubricValidationError(
                f"Dimension {dim['id']}: scoring must be an object"
            )

        missing_bands = [b for b in scoring_bands if b not in dim["scoring"]]
        if missing_bands:
            raise RubricValidationError(
                f"Dimension {dim['id']}: missing scoring bands: {', '.join(missing_bands)}"
            )

    # Validate total weight sums to 1.0 (within tolerance)
    if abs(total_weight - 1.0) > 0.01:
        raise RubricValidationError(
            f"Dimension weights sum to {total_weight:.4f}, expected 1.0 (±0.01)"
        )

    logger.debug(
        f"Rubric validation passed for role '{rubric_dict['role']}': "
        f"{len(dimensions)} dimensions, weights sum to {total_weight:.4f}"
    )


def load_rubric(role: str) -> dict[str, Any]:
    """
    Load rubric for specified role from filesystem.

    Uses in-memory cache for performance. Cache is populated on first access.

    Args:
        role: Role identifier ('ae', 'se', 'csm')

    Returns:
        Rubric dictionary with dimensions, criteria, and scoring

    Raises:
        RubricValidationError: If rubric is malformed
        FileNotFoundError: If rubric file doesn't exist
    """
    # Check cache first
    if role in _rubric_cache:
        logger.debug(f"Rubric cache hit for role '{role}'")
        return _rubric_cache[role]

    # Load from filesystem
    rubric_file = RUBRICS_DIR / f"{role}_rubric.json"

    if not rubric_file.exists():
        raise FileNotFoundError(
            f"Rubric file not found: {rubric_file}. "
            f"Valid roles: ae, se, csm"
        )

    logger.info(f"Loading rubric for role '{role}' from {rubric_file}")

    try:
        with open(rubric_file, "r") as f:
            rubric_dict = json.load(f)
    except json.JSONDecodeError as e:
        raise RubricValidationError(
            f"Failed to parse rubric JSON for role '{role}': {e}"
        )

    # Validate structure
    try:
        validate_rubric(rubric_dict)
    except RubricValidationError as e:
        logger.error(f"Rubric validation failed for role '{role}': {e}")
        raise

    # Cache and return
    _rubric_cache[role] = rubric_dict
    logger.info(
        f"Loaded rubric for {rubric_dict['role_name']}: "
        f"{len(rubric_dict['dimensions'])} dimensions, validation passed"
    )

    return rubric_dict


def reload_rubrics() -> None:
    """
    Clear cache and reload all rubrics from filesystem.

    Useful for development or when rubric files are updated.
    """
    global _rubric_cache

    logger.info("Reloading all rubrics from filesystem")
    _rubric_cache.clear()

    # Pre-load all known rubrics
    roles = ["ae", "se", "csm"]
    for role in roles:
        try:
            load_rubric(role)
        except Exception as e:
            logger.error(f"Failed to reload rubric for role '{role}': {e}")

    logger.info(f"Rubric cache reloaded: {len(_rubric_cache)} rubrics loaded")


def get_available_roles() -> list[str]:
    """
    Get list of available role identifiers.

    Returns:
        List of role identifiers (e.g., ['ae', 'se', 'csm'])
    """
    return ["ae", "se", "csm"]


def get_rubric_info(role: str) -> dict[str, Any]:
    """
    Get high-level rubric information without loading full rubric.

    Args:
        role: Role identifier

    Returns:
        Dict with role, role_name, and dimension count
    """
    rubric = load_rubric(role)
    return {
        "role": rubric["role"],
        "role_name": rubric["role_name"],
        "description": rubric.get("description", ""),
        "dimension_count": len(rubric["dimensions"]),
        "dimensions": [
            {
                "id": dim["id"],
                "name": dim["name"],
                "weight": dim["weight"]
            }
            for dim in rubric["dimensions"]
        ]
    }
