import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

// Bypass auth entirely in development when BYPASS_AUTH is set
const bypassAuth = process.env.NODE_ENV === "development" && process.env.BYPASS_AUTH === "true";

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhook(.*)", // For Clerk webhooks
  "/api/health(.*)", // Health check for container probes
]);

export default clerkMiddleware(async (auth, request) => {
  // In dev mode with BYPASS_AUTH, skip all auth checks
  if (bypassAuth) {
    return NextResponse.next();
  }

  // Protect all routes except public ones
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals, static files, and health check endpoint
    "/((?!_next|api/health|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes except health check
    "/(api(?!/health)|trpc)(.*)",
  ],
};
