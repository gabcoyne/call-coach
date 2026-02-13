"use client";

import { UserButton } from "@clerk/nextjs";
import { useUser } from "@/lib/hooks/use-auth";
import { Skeleton } from "@/components/ui/skeleton";
import { RoleBadge } from "@/components/ui/role-badge";
import { useCurrentUser } from "@/lib/hooks/use-current-user";

export function UserNav() {
  const { user, isLoaded } = useUser();
  const { data: currentUser } = useCurrentUser();

  if (!isLoaded) {
    return (
      <div className="flex items-center gap-3 px-4 py-3 border-t border-border">
        <Skeleton className="h-8 w-8 rounded-full" />
        <div className="flex-1 min-w-0">
          <Skeleton className="h-4 w-24 mb-1" />
          <Skeleton className="h-3 w-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 px-4 py-3 border-t border-border bg-card">
      <UserButton
        appearance={{
          elements: {
            avatarBox: "h-8 w-8",
          },
        }}
        afterSignOutUrl="/sign-in"
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className="text-sm font-medium text-foreground truncate">
            {user?.fullName || user?.primaryEmailAddress?.emailAddress}
          </p>
          {currentUser?.role && <RoleBadge role={currentUser.role} />}
        </div>
        <p className="text-xs text-muted-foreground truncate">
          {user?.primaryEmailAddress?.emailAddress}
        </p>
      </div>
    </div>
  );
}
