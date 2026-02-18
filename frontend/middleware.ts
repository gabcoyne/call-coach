import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for IAP-authenticated requests
 *
 * IAP handles authentication at the load balancer level.
 * This middleware extracts the IAP headers and makes them available.
 *
 * IAP Headers:
 * - X-Goog-Authenticated-User-Email: accounts.google.com:user@example.com
 * - X-Goog-Authenticated-User-Id: accounts.google.com:1234567890
 * - X-Goog-Iap-Jwt-Assertion: JWT token (can be verified)
 */

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // In production, IAP adds these headers
  // In development, we can bypass or mock them
  const bypassAuth = process.env.NODE_ENV === "development" && process.env.BYPASS_AUTH === "true";

  if (bypassAuth) {
    // Set mock IAP headers for development
    response.headers.set("x-iap-user-email", "george@prefect.io");
    response.headers.set("x-iap-user-id", "dev_user_george");
  } else {
    // Extract IAP headers and normalize them
    const iapEmail = request.headers.get("x-goog-authenticated-user-email");
    const iapUserId = request.headers.get("x-goog-authenticated-user-id");

    if (iapEmail) {
      // IAP email format: "accounts.google.com:user@example.com"
      const email = iapEmail.replace("accounts.google.com:", "");
      response.headers.set("x-iap-user-email", email);
    }

    if (iapUserId) {
      const userId = iapUserId.replace("accounts.google.com:", "");
      response.headers.set("x-iap-user-id", userId);
    }
  }

  return response;
}

export const config = {
  matcher: [
    // Skip Next.js internals and static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
