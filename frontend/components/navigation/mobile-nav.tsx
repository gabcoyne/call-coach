"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Search,
  Rss,
  User,
  Phone,
  Menu,
  X,
  Target,
  Users,
  Shield,
} from "lucide-react";
import { useCurrentUser } from "@/lib/hooks/use-current-user";
import { isManager, isAdmin } from "@/lib/rbac";

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

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { data: currentUser } = useCurrentUser();
  const userIsManager = isManager(currentUser);
  const userIsAdmin = isAdmin(currentUser);

  return (
    <div className="lg:hidden">
      {/* Mobile header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-gradient-to-r bg-prefect-gradient rounded-lg flex items-center justify-center">
            <Phone className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">Call Coach</h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <UserButton
            appearance={{
              elements: {
                avatarBox: "h-8 w-8",
              },
            }}
            afterSignOutUrl="/sign-in"
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(!isOpen)}
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="fixed inset-y-0 right-0 w-full max-w-sm border-l border-border bg-card">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 bg-gradient-to-r bg-prefect-gradient rounded-lg flex items-center justify-center">
                  <Phone className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-base font-bold text-foreground">Call Coach</h1>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                aria-label="Close menu"
              >
                <X className="h-6 w-6" />
              </Button>
            </div>

            <nav className="px-4 py-6 space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      "group flex items-center px-3 py-3 text-base font-medium rounded-md transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    )}
                  >
                    <item.icon
                      className={cn(
                        "mr-3 h-6 w-6 flex-shrink-0",
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
                  <div className="py-2 border-t border-border" />
                  {managerNavigation.map((item) => {
                    const isActive =
                      pathname === item.href || pathname?.startsWith(`${item.href}/`);
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={() => setIsOpen(false)}
                        className={cn(
                          "group flex items-center px-3 py-3 text-base font-medium rounded-md transition-colors",
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                        )}
                      >
                        <item.icon
                          className={cn(
                            "mr-3 h-6 w-6 flex-shrink-0",
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

              {/* Admin Navigation */}
              {userIsAdmin && (
                <>
                  {adminNavigation.map((item) => {
                    const isActive =
                      pathname === item.href || pathname?.startsWith(`${item.href}/`);
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={() => setIsOpen(false)}
                        className={cn(
                          "group flex items-center px-3 py-3 text-base font-medium rounded-md transition-colors",
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                        )}
                      >
                        <item.icon
                          className={cn(
                            "mr-3 h-6 w-6 flex-shrink-0",
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
          </div>
        </div>
      )}
    </div>
  );
}
