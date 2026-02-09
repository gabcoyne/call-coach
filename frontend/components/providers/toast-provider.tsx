'use client';

import { useToast } from '@/components/ui/use-toast';
import { Toaster } from '@/components/ui/toaster';

export function ToastProvider() {
  const { toasts, dismiss } = useToast();

  return <Toaster toasts={toasts} onRemove={dismiss} />;
}
