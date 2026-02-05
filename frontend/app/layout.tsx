import type { Metadata } from "next";
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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
