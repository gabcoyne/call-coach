'use client';

import { useEffect, useState } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToasterProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

const variantStyles = {
  default: {
    bg: 'bg-white border-gray-200',
    icon: <Info className="h-5 w-5 text-blue-500" />,
  },
  success: {
    bg: 'bg-green-50 border-green-200',
    icon: <CheckCircle className="h-5 w-5 text-green-600" />,
  },
  error: {
    bg: 'bg-red-50 border-red-200',
    icon: <AlertCircle className="h-5 w-5 text-red-600" />,
  },
  warning: {
    bg: 'bg-amber-50 border-amber-200',
    icon: <AlertTriangle className="h-5 w-5 text-amber-600" />,
  },
  info: {
    bg: 'bg-blue-50 border-blue-200',
    icon: <Info className="h-5 w-5 text-blue-600" />,
  },
};

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  const [isExiting, setIsExiting] = useState(false);
  const variant = toast.variant || 'default';
  const style = variantStyles[variant];

  useEffect(() => {
    const duration = toast.duration ?? 5000;
    if (duration === 0) return;

    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onRemove(toast.id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, onRemove]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => onRemove(toast.id), 300);
  };

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-lg border shadow-lg
        ${style.bg}
        transition-all duration-300 ease-in-out
        ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
      `}
      role="alert"
    >
      {style.icon}
      <div className="flex-1 min-w-0">
        {toast.title && (
          <div className="font-semibold text-sm text-gray-900 mb-1">{toast.title}</div>
        )}
        {toast.description && (
          <div className="text-sm text-gray-700">{toast.description}</div>
        )}
      </div>
      <button
        onClick={handleClose}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close notification"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export function Toaster({ toasts, onRemove }: ToasterProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="pointer-events-auto space-y-2">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </div>
    </div>
  );
}
