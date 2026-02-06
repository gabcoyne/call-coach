"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbItem {
  label: string;
  href: string;
}

function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const paths = pathname.split("/").filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: "Home", href: "/" }];

  let currentPath = "";
  paths.forEach((path, index) => {
    currentPath += `/${path}`;

    // Format the label (capitalize and replace hyphens)
    let label = path.charAt(0).toUpperCase() + path.slice(1);
    label = label.replace(/-/g, " ");

    // Special handling for known routes
    if (path === "dashboard") label = "Dashboard";
    if (path === "search") label = "Search";
    if (path === "feed") label = "Feed";
    if (path === "calls") label = "Calls";
    if (path === "profile") label = "Profile";

    // Don't add href for the last item (current page)
    breadcrumbs.push({
      label,
      href: index === paths.length - 1 ? "" : currentPath,
    });
  });

  return breadcrumbs;
}

export function Breadcrumb() {
  const pathname = usePathname();

  // Don't show breadcrumbs on home page or simple routes
  if (!pathname || pathname === "/" || pathname.split("/").filter(Boolean).length <= 1) {
    return null;
  }

  const breadcrumbs = generateBreadcrumbs(pathname);

  return (
    <nav className="flex items-center space-x-2 text-sm text-muted-foreground px-4 py-3 border-b border-border bg-card/50">
      {breadcrumbs.map((item, index) => (
        <div key={item.href || item.label} className="flex items-center">
          {index > 0 && <ChevronRight className="h-4 w-4 mx-2 flex-shrink-0" />}
          {index === 0 ? (
            <Link
              href={item.href}
              className="flex items-center hover:text-foreground transition-colors"
            >
              <Home className="h-4 w-4" />
            </Link>
          ) : item.href ? (
            <Link href={item.href} className="hover:text-foreground transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
