import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Toaster } from '../toaster';
import type { Toast } from '../toaster';

describe('Toaster', () => {
  const mockOnRemove = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  describe('Toast Rendering', () => {
    it('renders nothing when toasts array is empty', () => {
      const { container } = render(<Toaster toasts={[]} onRemove={mockOnRemove} />);
      expect(container.firstChild).toBeNull();
    });

    it('renders a single toast', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Success',
          description: 'Operation completed',
          variant: 'success',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      expect(screen.getByText('Success')).toBeInTheDocument();
      expect(screen.getByText('Operation completed')).toBeInTheDocument();
    });

    it('renders multiple toasts', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Success',
          description: 'First operation',
          variant: 'success',
        },
        {
          id: 'toast-2',
          title: 'Error',
          description: 'Second operation failed',
          variant: 'error',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      expect(screen.getByText('Success')).toBeInTheDocument();
      expect(screen.getByText('First operation')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Second operation failed')).toBeInTheDocument();
    });

    it('renders toast with title only', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Title Only',
          variant: 'info',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      expect(screen.getByText('Title Only')).toBeInTheDocument();
    });

    it('renders toast with description only', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          description: 'Description only',
          variant: 'info',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      expect(screen.getByText('Description only')).toBeInTheDocument();
    });
  });

  describe('Toast Variants', () => {
    it('applies correct styles for success variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Success',
          variant: 'success',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('bg-green-50');
    });

    it('applies correct styles for error variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Error',
          variant: 'error',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('bg-red-50');
    });

    it('applies correct styles for warning variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Warning',
          variant: 'warning',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('bg-amber-50');
    });

    it('applies correct styles for info variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Info',
          variant: 'info',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('bg-blue-50');
    });

    it('applies default styles when variant is not specified', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Default',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('bg-white');
    });
  });

  describe('Toast Auto-dismiss', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    it('auto-dismisses after default duration (5 seconds)', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Auto-dismiss',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      expect(mockOnRemove).not.toHaveBeenCalled();

      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Wait for animation delay
      act(() => {
        jest.advanceTimersByTime(300);
      });

      expect(mockOnRemove).toHaveBeenCalledWith('toast-1');
    });

    it('auto-dismisses after custom duration', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Custom duration',
          duration: 2000,
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      act(() => {
        jest.advanceTimersByTime(2000);
      });

      act(() => {
        jest.advanceTimersByTime(300);
      });

      expect(mockOnRemove).toHaveBeenCalledWith('toast-1');
    });

    it('does not auto-dismiss when duration is 0', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'No auto-dismiss',
          duration: 0,
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      act(() => {
        jest.advanceTimersByTime(10000);
      });

      expect(mockOnRemove).not.toHaveBeenCalled();
    });
  });

  describe('Toast Manual Dismiss', () => {
    it('calls onRemove when close button is clicked', async () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Closeable',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const closeButton = screen.getByLabelText('Close notification');

      act(() => {
        closeButton.click();
      });

      // onRemove should be called after animation delay
      await waitFor(() => {
        expect(mockOnRemove).toHaveBeenCalledWith('toast-1');
      }, { timeout: 500 });
    });

    it('shows exit animation before removing', async () => {
      jest.useFakeTimers();

      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Animated exit',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const closeButton = screen.getByLabelText('Close notification');

      act(() => {
        closeButton.click();
      });

      // Should not call onRemove immediately
      expect(mockOnRemove).not.toHaveBeenCalled();

      // Should call after animation delay
      await act(async () => {
        jest.advanceTimersByTime(300);
      });

      expect(mockOnRemove).toHaveBeenCalledWith('toast-1');

      jest.useRealTimers();
    });
  });

  describe('Toast Icons', () => {
    it('renders CheckCircle icon for success variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Success',
          variant: 'success',
        },
      ];

      const { container } = render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      // Check for SVG icon presence
      const icons = container.querySelectorAll('svg');
      expect(icons.length).toBeGreaterThan(0);
    });

    it('renders AlertCircle icon for error variant', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Error',
          variant: 'error',
        },
      ];

      const { container } = render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const icons = container.querySelectorAll('svg');
      expect(icons.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('has correct ARIA attributes', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Accessible',
        },
      ];

      const { container } = render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toastContainer = container.querySelector('[aria-live]');
      expect(toastContainer).toHaveAttribute('aria-live', 'polite');
      expect(toastContainer).toHaveAttribute('aria-atomic', 'true');
    });

    it('marks individual toasts with role="alert"', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Alert',
        },
      ];

      render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toast = screen.getByRole('alert');
      expect(toast).toBeInTheDocument();
    });
  });

  describe('Positioning', () => {
    it('renders toasts in top-right corner', () => {
      const toasts: Toast[] = [
        {
          id: 'toast-1',
          title: 'Positioned',
        },
      ];

      const { container } = render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const toastContainer = container.querySelector('[class*="fixed"]');
      expect(toastContainer).toHaveClass('top-4');
      expect(toastContainer).toHaveClass('right-4');
    });

    it('stacks multiple toasts vertically', () => {
      const toasts: Toast[] = [
        { id: 'toast-1', title: 'First' },
        { id: 'toast-2', title: 'Second' },
      ];

      const { container } = render(<Toaster toasts={toasts} onRemove={mockOnRemove} />);

      const stackContainer = container.querySelector('[class*="space-y"]');
      expect(stackContainer).toBeInTheDocument();
    });
  });
});
