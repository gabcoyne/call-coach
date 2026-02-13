"use client";

import { useAuth } from "@/lib/hooks/use-auth";
import { SettingsNav } from "@/components/settings/settings-nav";
import { Card } from "@/components/ui/card";

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="p-6">
        <div className="h-64 flex items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="p-6">
        <Card className="p-6">
          <p className="text-muted-foreground">Please sign in to access settings.</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 p-6">
      {/* Settings Navigation Sidebar */}
      <div className="md:col-span-1">
        <div className="sticky top-6">
          <h2 className="text-lg font-semibold text-foreground mb-4 hidden md:block">Settings</h2>
          <Card className="p-0 overflow-hidden">
            <SettingsNav />
          </Card>
        </div>
      </div>

      {/* Settings Content */}
      <div className="md:col-span-3">
        <div className="space-y-6">{children}</div>
      </div>
    </div>
  );
}
