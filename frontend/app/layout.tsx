import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { Sidebar } from "@/components/navigation/sidebar";
import { MobileNav } from "@/components/navigation/mobile-nav";
import { UserNav } from "@/components/navigation/user-nav";
import { Breadcrumb } from "@/components/navigation/breadcrumb";
import { WebVitals } from "@/components/analytics/WebVitals";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gong Call Coaching",
  description: "AI-powered sales coaching for Prefect teams",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className="min-h-screen bg-background font-sans antialiased">
          <WebVitals />
          <div className="flex h-screen overflow-hidden">
            {/* Desktop Sidebar with User Nav */}
            <div className="hidden lg:flex lg:flex-shrink-0">
              <div className="flex w-64 flex-col">
                <Sidebar />
                <UserNav />
              </div>
            </div>

            {/* Main Content Area */}
            <div className="flex flex-1 flex-col overflow-hidden">
              {/* Mobile Navigation */}
              <MobileNav />

              {/* Breadcrumb Navigation */}
              <Breadcrumb />

              {/* Page Content */}
              <main className="flex-1 overflow-y-auto bg-background">
                {children}
              </main>
            </div>
          </div>
        </body>
      </html>
    </ClerkProvider>
  );
}
