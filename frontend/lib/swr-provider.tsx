/**
 * SWR Provider Component
 *
 * Wraps the application with SWR configuration and provides global context.
 * Should be added to the root layout.tsx file.
 */

"use client";

import { SWRConfig } from "swr";
import { swrConfig } from "./swr-config";

interface SWRProviderProps {
  children: React.ReactNode;
}

/**
 * SWR Provider component
 *
 * Provides global SWR configuration to all child components.
 * This includes default fetcher, revalidation settings, and error retry logic.
 *
 * @example
 * ```tsx
 * // In app/layout.tsx
 * export default function RootLayout({ children }: { children: React.ReactNode }) {
 *   return (
 *     <html lang="en">
 *       <body>
 *         <AuthProvider>
 *           <SWRProvider>
 *             {children}
 *           </SWRProvider>
 *         </AuthProvider>
 *       </body>
 *     </html>
 *   );
 * }
 * ```
 */
export function SWRProvider({ children }: SWRProviderProps) {
  return <SWRConfig value={swrConfig}>{children}</SWRConfig>;
}
