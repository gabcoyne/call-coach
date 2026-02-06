"""
Vercel serverless function for daily Gong sync cron job.

Scheduled to run daily at 6am via vercel.json cron configuration.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for daily sync cron job."""

    def do_GET(self):
        """Handle GET request from Vercel cron."""
        try:
            # Import here to avoid cold start issues
            from flows.daily_gong_sync import main

            # Execute sync
            logger.info("Vercel cron triggered daily sync")
            result = main()

            # Return success response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Sync failed in Vercel cron: {e}", exc_info=True)

            # Return error response
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "status": "error",
                        "error": str(e),
                        "message": "Daily sync failed",
                    }
                ).encode()
            )
