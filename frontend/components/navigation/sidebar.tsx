"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "@/lib/hooks/use-auth";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Search,
  Rss,
  User,
  Phone,
  Target,
  Settings,
  Shield,
  Users,
} from "lucide-react";
import { useCurrentUser } from "@/lib/hooks/use-current-user";
import { isManager } from "@/lib/rbac";

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Search",
    href: "/search",
    icon: Search,
  },
  {
    name: "Feed",
    href: "/feed",
    icon: Rss,
  },
  {
    name: "Calls",
    href: "/calls",
    icon: Phone,
  },
  {
    name: "Opportunities",
    href: "/opportunities",
    icon: Target,
  },
  {
    name: "Profile",
    href: "/profile",
    icon: User,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

const managerNavigation = [
  {
    name: "My Team",
    href: "/team/dashboard",
    icon: Users,
  },
];

const adminNavigation = [
  {
    name: "Admin",
    href: "/admin",
    icon: Shield,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useUser();
  const { data: currentUser } = useCurrentUser();
  const userIsManager = isManager(currentUser);

  return (
    <div className="flex flex-col flex-grow border-r border-border bg-card overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center flex-shrink-0 px-6 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-prefect-gradient rounded-lg flex items-center justify-center shadow-sm">
            <Phone className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">Call Coach</h1>
            <p className="text-xs text-muted-foreground">by Prefect</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive
                    ? "text-primary-foreground"
                    : "text-muted-foreground group-hover:text-accent-foreground"
                )}
              />
              {item.name}
            </Link>
          );
        })}

        {/* Manager Navigation */}
        {userIsManager && (
          <>
            <div className="py-2 border-t border-border mt-4" />
            {managerNavigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <item.icon
                    className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0",
                      isActive
                        ? "text-primary-foreground"
                        : "text-muted-foreground group-hover:text-accent-foreground"
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </>
        )}

        {/* Admin Navigation (Manager only) */}
        {userIsManager && (
          <>
            {adminNavigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <item.icon
                    className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0",
                      isActive
                        ? "text-primary-foreground"
                        : "text-muted-foreground group-hover:text-accent-foreground"
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </>
        )}
      </nav>

      {/* Footer with version */}
      <div className="flex-shrink-0 px-6 py-2 border-t border-border">
        <p className="text-xs text-muted-foreground">v0.1.0</p>
      </div>
    </div>
  );
}
