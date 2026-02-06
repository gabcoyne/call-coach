"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ShieldAlert, Home, ArrowLeft } from "lucide-react";

interface ForbiddenPageProps {
  message?: string;
  returnUrl?: string;
}

/**
 * 403 Forbidden Error Page
 *
 * Displayed when a user attempts to access a resource they don't have permission to view.
 * Common scenarios:
 * - Rep trying to view another rep's dashboard
 * - Rep trying to access manager-only features
 * - Unauthenticated access attempts to protected resources
 */
export default function ForbiddenPage({
  message = "You don't have permission to access this page",
  returnUrl = "/dashboard",
}: ForbiddenPageProps) {
  const router = useRouter();

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <ShieldAlert className="h-8 w-8 text-destructive" />
            </div>
          </div>
          <CardTitle className="text-2xl">Access Denied</CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-6xl font-bold text-muted-foreground/20">403</p>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              If you believe this is an error, please contact your manager or system administrator.
            </p>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-2">
          <Button onClick={() => router.back()} variant="outline" className="w-full gap-2">
            <ArrowLeft className="h-4 w-4" />
            Go back
          </Button>
          <Button asChild className="w-full gap-2">
            <Link href={returnUrl}>
              <Home className="h-4 w-4" />
              Go to dashboard
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
