"use client";

import { createContext, useContext, ReactNode } from "react";

/**
 * Mock user for development when BYPASS_AUTH is enabled
 */
export const DEV_USER = {
  id: "dev_user_george",
  firstName: "George",
  lastName: "Coyne",
  fullName: "George Coyne",
  emailAddresses: [{ emailAddress: "george@prefect.io" }],
  publicMetadata: {
    role: "manager", // Can be "rep", "manager", or "admin"
    title: "Director of Engineering, GTM",
  },
  imageUrl: null,
};

interface DevAuthContextType {
  user: typeof DEV_USER | null;
  isLoaded: boolean;
  isSignedIn: boolean;
}

const DevAuthContext = createContext<DevAuthContextType>({
  user: null,
  isLoaded: false,
  isSignedIn: false,
});

export function DevAuthProvider({ children }: { children: ReactNode }) {
  return (
    <DevAuthContext.Provider
      value={{
        user: DEV_USER,
        isLoaded: true,
        isSignedIn: true,
      }}
    >
      {children}
    </DevAuthContext.Provider>
  );
}

export function useDevAuth() {
  return useContext(DevAuthContext);
}

/**
 * Hook that returns dev user when BYPASS_AUTH is enabled,
 * falls back to Clerk's useUser otherwise
 */
export function useDevUser() {
  const devAuth = useContext(DevAuthContext);
  return {
    user: devAuth.user,
    isLoaded: devAuth.isLoaded,
    isSignedIn: devAuth.isSignedIn,
  };
}
