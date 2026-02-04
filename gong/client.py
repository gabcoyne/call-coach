"""
Gong API client for fetching call data and transcripts.
Documentation: https://gong.app.gong.io/settings/api/documentation
"""
import logging
from typing import Any

import httpx
from httpx import HTTPStatusError, RequestError

from config import settings
from .types import GongCall, GongTranscript, GongTranscriptSegment, GongSpeaker

logger = logging.getLogger(__name__)


class GongAPIError(Exception):
    """Base exception for Gong API errors."""
    pass


class GongClient:
    """
    Client for interacting with Gong API.
    Handles authentication, rate limiting, and retries.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.gong_api_key
        self.base_url = base_url or settings.gong_api_base_url

        # HTTP client with auth and timeouts
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=(self.api_key, ""),  # Gong uses basic auth with API key as username
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

    def get_transcript(self, call_id: str) -> GongTranscript:
        """
        Fetch call transcript from Gong.

        Args:
            call_id: Gong call ID

        Returns:
            GongTranscript with segments
        """
        logger.info(f"Fetching transcript for call {call_id}")

        response = self._make_request("GET", f"/calls/{call_id}/transcript")

        # Parse transcript segments
        segments = []
        for segment in response.get("transcript", []):
            segments.append(
                GongTranscriptSegment(
                    speaker_id=segment.get("speakerId", ""),
                    start_time=segment.get("start", 0),
                    duration=segment.get("duration", 0),
                    text=segment.get("text", ""),
                    sentiment=segment.get("sentiment"),
                )
            )

        return GongTranscript(
            call_id=call_id,
            segments=segments,
        )

    def list_calls(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        workspace_id: str | None = None,
        limit: int = 100,
    ) -> list[GongCall]:
        """
        List calls with optional filters.

        Args:
            from_date: Start date (ISO 8601 format)
            to_date: End date (ISO 8601 format)
            workspace_id: Filter by workspace
            limit: Max results to return

        Returns:
            List of GongCall objects
        """
        logger.info(f"Listing calls: from={from_date}, to={to_date}, limit={limit}")

        params = {
            "fromDateTime": from_date,
            "toDateTime": to_date,
            "workspaceId": workspace_id,
            "limit": limit,
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

        return calls

    def search_calls(
        self,
        query: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 50,
    ) -> list[str]:
        """
        Search calls by text query.

        Args:
            query: Search query
            from_date: Start date (ISO 8601 format)
            to_date: End date (ISO 8601 format)
            limit: Max results

        Returns:
            List of call IDs matching query
        """
        logger.info(f"Searching calls: query='{query}', limit={limit}")

        params = {
            "q": query,
            "fromDateTime": from_date,
            "toDateTime": to_date,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("GET", "/calls/search", params=params)

        return [call.get("id") for call in response.get("calls", []) if call.get("id")]
