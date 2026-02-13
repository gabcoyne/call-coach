"use client";

import { useState, useCallback } from "react";
import type { Toast } from "./toaster";

let toastCounter = 0;
let listeners: ((toasts: Toast[]) => void)[] = [];
let toastsState: Toast[] = [];

function generateId() {
  return `toast-${++toastCounter}`;
}

function notifyListeners() {
  listeners.forEach((listener) => listener(toastsState));
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>(toastsState);

  // Subscribe to global toast state
  useState(() => {
    const listener = (newToasts: Toast[]) => {
      setToasts(newToasts);
    };
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  });

  const toast = useCallback(
    (options: {
      title?: string;
      description?: string;
      variant?: "default" | "success" | "error" | "warning" | "info" | "destructive";
      duration?: number;
    }) => {
      // Map 'destructive' to 'error' for shadcn/ui compatibility
      const mappedOptions = {
        ...options,
        variant: options.variant === "destructive" ? "error" : options.variant,
      };
      const id = generateId();
      const newToast: Toast = {
        id,
        ...mappedOptions,
      };
      toastsState = [...toastsState, newToast];
      notifyListeners();
      return id;
    },
    []
  );

  const dismiss = useCallback((id: string) => {
    toastsState = toastsState.filter((t) => t.id !== id);
    notifyListeners();
  }, []);

  return {
    toasts,
    toast,
    dismiss,
  };
}
