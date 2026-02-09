'use client';

import useSWR from 'swr';
import { useAuth, useUser } from '@clerk/nextjs';

const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || 'http://localhost:8000';

export interface CurrentUser {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'rep';
}

export function useCurrentUser() {
  const { getToken, userId } = useAuth();
  const { user } = useUser();

  // Get email from Clerk user for the X-User-Email header
  const email = user?.emailAddresses[0]?.emailAddress;

  return useSWR<CurrentUser>(
    userId && email ? ['currentUser', userId] : null,
    async () => {
      const res = await fetch(`${MCP_BACKEND_URL}/api/v1/users/me`, {
        headers: {
          'X-User-Email': email!,  // Use Clerk email for backend auth
        }
      });

      if (!res.ok) {
        throw new Error('Failed to fetch current user');
      }

      return res.json();
    },
    {
      // Revalidate every 5 minutes (user data doesn't change frequently)
      refreshInterval: 5 * 60 * 1000,
      // Revalidate on focus to catch role changes
      revalidateOnFocus: true,
      // Retry on error
      errorRetryCount: 3,
      errorRetryInterval: 1000,
      // Keep previous data while revalidating
      keepPreviousData: true,
    }
  );
}
