"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  User,
  Bell,
  Sliders,
  Lock,
} from "lucide-react";

const settingsNavigation = [
  {
    name: "Profile",
    href: "/settings/profile",
    icon: User,
    description: "Manage your account information",
  },
  {
    name: "Notifications",
    href: "/settings/notifications",
    icon: Bell,
    description: "Email and notification preferences",
  },
  {
    name: "Preferences",
    href: "/settings/preferences",
    icon: Sliders,
    description: "Customize your experience",
  },
  {
    name: "Data & Privacy",
    href: "/settings/data",
    icon: Lock,
    description: "Export data and privacy settings",
  },
];

export function SettingsNav() {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {settingsNavigation.map((item) => {
        const isActive = pathname === item.href;
        const Icon = item.icon;

        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <Icon className={cn("h-5 w-5 flex-shrink-0", isActive ? "text-primary-foreground" : "")} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{item.name}</p>
              <p className={cn("text-xs truncate", isActive ? "text-primary-foreground/80" : "text-muted-foreground")}>
                {item.description}
              </p>
            </div>
          </Link>
        );
      })}
    </nav>
  );
}
