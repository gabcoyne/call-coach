"""
Gong API client for fetching call data and transcripts.
Documentation: https://gong.app.gong.io/settings/api/documentation
"""
import logging
from typing import Any

import httpx
from httpx import HTTPStatusError, RequestError

from config import settings
from .types import GongCall, GongTranscript, GongMonologue, GongSentence, GongSpeaker

logger = logging.getLogger(__name__)


class GongAPIError(Exception):
    """Base exception for Gong API errors."""
    pass


class GongClient:
    """
    Client for interacting with Gong API.
    Handles authentication, rate limiting, and retries.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize Gong API client.

        Gong authentication requires BOTH access key and secret key in Basic Auth format:
        Authorization: Basic base64(access_key:secret_key)

        Args:
            api_key: Gong access key (e.g., "UQ4SK2LPUPBCFN7Q...")
            api_secret: Gong secret key / JWT token (e.g., "eyJhbGciOiJIUzI1NiJ9...")
            base_url: Tenant-specific base URL (e.g., "https://us-79647.api.gong.io/v2")
        """
        self.api_key = api_key or settings.gong_api_key
        self.api_secret = api_secret or settings.gong_api_secret
        self.base_url = base_url or settings.gong_api_base_url

        # HTTP client with Basic Auth (access_key:secret_key)
        # This is the correct authentication method for Gong API v2
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=(self.api_key, self.api_secret),  # Basic Auth: key:secret
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an authenticated request to Gong API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/calls")
            params: Query parameters
            json_data: JSON body

        Returns:
            Response JSON as dict

        Raises:
            GongAPIError: If request fails
        """
        try:
            response = self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            logger.error(f"Gong API HTTP error: {e.response.status_code} - {e.response.text}")
            raise GongAPIError(f"HTTP {e.response.status_code}: {e.response.text}") from e

        except RequestError as e:
            logger.error(f"Gong API request error: {e}")
            raise GongAPIError(f"Request failed: {e}") from e

    def get_call(self, call_id: str) -> GongCall:
        """
        Fetch call metadata from Gong.

        Args:
            call_id: Gong call ID

        Returns:
            GongCall object with call metadata
        """
        logger.info(f"Fetching call metadata for {call_id}")

        response = self._make_request("GET", f"/calls/{call_id}")

        # Extract call data (structure varies by endpoint)
        call_data = response.get("call") or response

        # Parse speakers/participants
        participants = []
        for participant in call_data.get("participants", []):
            participants.append(
                GongSpeaker(
                    speaker_id=participant.get("id", ""),
                    name=participant.get("name", "Unknown"),
                    email=participant.get("emailAddress"),
                    title=participant.get("title"),
                    is_internal=participant.get("isInternal", False),
                    talk_time_seconds=participant.get("speakingTime", 0),
                )
            )

        return GongCall(
            id=call_data.get("id", call_id),
            title=call_data.get("title"),
            scheduled=call_data.get("scheduled"),
            started=call_data.get("started"),
            duration=call_data.get("duration"),
            primary_user_id=call_data.get("primaryUserId"),
            direction=call_data.get("direction"),
            system=call_data.get("system"),
            scope=call_data.get("scope"),
            media=call_data.get("media"),
            language=call_data.get("language"),
            workspace_id=call_data.get("workspaceId"),
            url=call_data.get("url"),
            participants=participants,
            custom_data=call_data.get("customData"),
        )

    def get_transcript(
        self,
        call_id: str,
        from_datetime: str | None = None,
        to_datetime: str | None = None,
        call_metadata: GongCall | None = None,
    ) -> GongTranscript:
        """
        Fetch call transcript from Gong using the official POST /v2/calls/transcript endpoint.

        The API requires a date range filter. If not provided, uses a wide range (2020-2030).
        To fetch transcripts for specific calls, you must know their approximate date or
        provide a wide enough date range.

        Args:
            call_id: Gong call ID
            from_datetime: ISO 8601 datetime string (e.g., "2024-01-01T00:00:00Z")
            to_datetime: ISO 8601 datetime string (e.g., "2024-12-31T23:59:59Z")

        Returns:
            GongTranscript with monologues

        Raises:
            GongAPIError: If call not found or date range doesn't include call
        """
        logger.info(f"Fetching transcript for call {call_id}")

        # Try to use call metadata for more efficient date range
        if call_metadata and call_metadata.started and not from_datetime:
            # Use call start date +/- 1 day for more efficient query
            from datetime import timedelta
            call_start = call_metadata.started
            from_datetime = (call_start - timedelta(days=1)).isoformat()
            to_datetime = (call_start + timedelta(days=1)).isoformat()
            logger.info(f"Using call date range: {from_datetime} to {to_datetime}")
        elif not from_datetime:
            # Fall back to wide date range (inefficient but works)
            from_datetime = "2020-01-01T00:00:00Z"
            to_datetime = "2030-01-01T00:00:00Z"
            logger.warning(
                "Using wide date range for transcript fetch. "
                "For better performance, provide call_metadata or from_datetime/to_datetime."
            )

        response = self._make_request(
            "POST",
            "/calls/transcript",  # Base URL already includes /v2
            json_data={
                "filter": {
                    "callIds": [call_id],
                    "fromDateTime": from_datetime,
                    "toDateTime": to_datetime,
                }
            },
        )

        # Extract transcript for this call
        call_transcripts = response.get("callTranscripts", [])
        if not call_transcripts:
            raise GongAPIError(
                f"No transcript found for call {call_id}. "
                f"Verify call exists and date range ({from_datetime} to {to_datetime}) includes call."
            )

        transcript_data = call_transcripts[0]  # Should only be one since we filtered by callIds

        # Parse monologues
        monologues = []
        for monologue_data in transcript_data.get("transcript", []):
            sentences = []
            for sentence_data in monologue_data.get("sentences", []):
                sentences.append(
                    GongSentence(
                        start=sentence_data.get("start", 0),
                        end=sentence_data.get("end", 0),
                        text=sentence_data.get("text", ""),
                    )
                )

            monologues.append(
                GongMonologue(
                    speaker_id=monologue_data.get("speakerId", ""),
                    topic=monologue_data.get("topic"),
                    sentences=sentences,
                )
            )

        return GongTranscript(
            call_id=call_id,
            monologues=monologues,
        )

    def list_calls(
        self,
        from_date: str,
        to_date: str,
        workspace_id: str | None = None,
        cursor: str | None = None,
    ) -> tuple[list[GongCall], str | None]:
        """
        List calls with pagination support using cursor-based iteration.

        The Gong API requires both fromDateTime and toDateTime parameters.
        Results are paginated - use the returned cursor to fetch next page.

        Args:
            from_date: Start date (ISO 8601 format, REQUIRED)
                      e.g., "2024-01-01T00:00:00Z"
            to_date: End date (ISO 8601 format, REQUIRED)
                    e.g., "2024-12-31T23:59:59Z"
            workspace_id: Optional workspace filter
            cursor: Pagination cursor from previous response

        Returns:
            Tuple of (list of GongCall objects, next cursor or None if no more pages)

        Example:
            # First page
            calls, cursor = client.list_calls("2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")

            # Next page
            if cursor:
                more_calls, next_cursor = client.list_calls(
                    "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z", cursor=cursor
                )
        """
        logger.info(f"Listing calls: from={from_date}, to={to_date}, cursor={cursor[:20] if cursor else None}...")

        params = {
            "fromDateTime": from_date,
            "toDateTime": to_date,
            "workspaceId": workspace_id,
            "cursor": cursor,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("GET", "/calls", params=params)

        calls = []
        for call_data in response.get("calls", []):
            calls.append(
                GongCall(
                    id=call_data.get("id", ""),
                    title=call_data.get("title"),
                    scheduled=call_data.get("scheduled"),
                    started=call_data.get("started"),
                    duration=call_data.get("duration"),
                    direction=call_data.get("direction"),
                    system=call_data.get("system"),
                    scope=call_data.get("scope"),
                )
            )

        # Extract cursor for next page (if any)
        next_cursor = response.get("records", {}).get("cursor")

        return calls, next_cursor

    def search_calls(
        self,
        query: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 50,
    ) -> list[str]:
        """
        Search calls by text query.

        **WARNING: This endpoint does not exist in the official Gong API v2 specification.**

        The Gong API does not provide a text search endpoint. To find calls, use `list_calls()`
        with date range filters, then filter results client-side.

        Args:
            query: Search query
            from_date: Start date (ISO 8601 format)
            to_date: End date (ISO 8601 format)
            limit: Max results

        Returns:
            List of call IDs matching query

        Raises:
            NotImplementedError: This endpoint doesn't exist in Gong API v2
        """
        raise NotImplementedError(
            "Gong API v2 does not provide a /calls/search endpoint. "
            "Use list_calls() with date filters and filter results client-side instead. "
            "See .openspec/GONG_CLIENT_AUDIT.md for details."
        )
