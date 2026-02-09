import { CurrentUser } from '@/lib/hooks/use-current-user';

export function isManager(user?: CurrentUser): boolean {
  return user?.role === 'manager' || user?.role === 'admin';
}

export function isAdmin(user?: CurrentUser): boolean {
  return user?.role === 'admin';
}

export function canViewCall(user: CurrentUser, callOwnerEmail: string): boolean {
  if (isManager(user)) return true; // Managers see all
  return user.email === callOwnerEmail; // Reps see only their own
}

export function canViewRep(user: CurrentUser, repEmail: string): boolean {
  if (isManager(user)) return true;
  return user.email === repEmail;
}
