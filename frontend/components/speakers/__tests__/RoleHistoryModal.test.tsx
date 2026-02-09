import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RoleHistoryModal } from '../RoleHistoryModal';

const mockHistoryEntries = [
  {
    id: 'history-1',
    speaker_id: 'speaker-1',
    old_role: null,
    new_role: 'ae',
    changed_by: 'admin@prefect.io',
    changed_at: '2024-01-15T10:30:00Z',
    reason: null,
  },
  {
    id: 'history-2',
    speaker_id: 'speaker-1',
    old_role: 'ae',
    new_role: 'se',
    changed_by: 'manager@prefect.io',
    changed_at: '2024-01-20T14:45:00Z',
    reason: 'Moved to solutions engineering team',
  },
  {
    id: 'history-3',
    speaker_id: 'speaker-1',
    old_role: 'se',
    new_role: null,
    changed_by: 'admin@prefect.io',
    changed_at: '2024-01-25T09:15:00Z',
    reason: null,
  },
];

describe('RoleHistoryModal', () => {
  const defaultProps = {
    speakerId: 'speaker-1',
    speakerName: 'John Doe',
    speakerEmail: 'john@prefect.io',
    isOpen: true,
    onClose: jest.fn(),
    userEmail: 'admin@prefect.io',
  };

  beforeEach(() => {
    global.fetch = jest.fn((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHistoryEntries),
        });
      }
      return Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Not found' }),
      });
    }) as jest.Mock;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Modal Display', () => {
    it('renders modal when isOpen is true', () => {
      render(<RoleHistoryModal {...defaultProps} />);

      expect(screen.getByText('Role Change History')).toBeInTheDocument();
    });

    it('displays speaker name and email', () => {
      render(<RoleHistoryModal {...defaultProps} />);

      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('(john@prefect.io)')).toBeInTheDocument();
    });

    it('does not render when isOpen is false', () => {
      render(<RoleHistoryModal {...defaultProps} isOpen={false} />);

      expect(screen.queryByText('Role Change History')).not.toBeInTheDocument();
    });
  });

  describe('History Entries', () => {
    it('fetches and displays role history on open', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/speakers/speaker-1/history'),
          expect.any(Object)
        );
      });

      await waitFor(() => {
        // Multiple role badges appear in history, so use getAllByText
        expect(screen.getAllByText('Account Executive').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Sales Engineer').length).toBeGreaterThan(0);
      });
    });

    it('displays role transitions with arrow icons', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getAllByText('Account Executive').length).toBeGreaterThan(0);
      });

      // Check for "None -> AE" transition
      const noneLabels = screen.getAllByText('None');
      expect(noneLabels.length).toBeGreaterThan(0);
    });

    it('shows changed_by information for each entry', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        // Email addresses might appear multiple times in history
        expect(screen.getAllByText('admin@prefect.io').length).toBeGreaterThan(0);
        expect(screen.getAllByText('manager@prefect.io').length).toBeGreaterThan(0);
      });
    });

    it('displays formatted timestamps', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        // Check that dates are rendered (format may vary based on locale)
        const dates = screen.getAllByText(/Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec/i);
        expect(dates.length).toBeGreaterThan(0);
      });
    });

    it('shows reason when provided', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/Moved to solutions engineering team/i)).toBeInTheDocument();
      });
    });

    it('does not show reason field when null', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getAllByText('Account Executive').length).toBeGreaterThan(0);
      });

      // First entry has no reason, so "Reason:" label should only appear once (for the entry that has a reason)
      const reasonLabels = screen.queryAllByText(/Reason:/i);
      expect(reasonLabels).toHaveLength(1);
    });
  });

  describe('Loading State', () => {
    it('shows loading skeletons while fetching', () => {
      render(<RoleHistoryModal {...defaultProps} />);

      // Check for multiple skeleton loaders
      const skeletons = document.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('hides loading state after data is loaded', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getAllByText('Account Executive').length).toBeGreaterThan(0);
      });

      const skeletons = document.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBe(0);
    });
  });

  describe('Empty State', () => {
    it('shows empty state message when no history exists', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });

      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/No role changes recorded/i)).toBeInTheDocument();
      });
    });

    it('displays clock icon in empty state', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });

      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/No role changes recorded/i)).toBeInTheDocument();
      });

      // Clock icon should be present
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when fetch fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load history/i)).toBeInTheDocument();
      });
    });

    it('shows retry button on error', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
      });
    });

    it('retries fetch when retry button is clicked', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load history/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /Retry/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Modal Interaction', () => {
    it('calls onClose when close button is clicked', async () => {
      const onClose = jest.fn();
      render(<RoleHistoryModal {...defaultProps} onClose={onClose} />);

      await waitFor(() => {
        expect(screen.getByText('Role Change History')).toBeInTheDocument();
      });

      // Find all "Close" buttons (there's one in header X and one at bottom)
      const closeButtons = screen.getAllByRole('button', { name: 'Close' });
      expect(closeButtons.length).toBeGreaterThan(0);

      // Click the first one
      fireEvent.click(closeButtons[0]);

      expect(onClose).toHaveBeenCalled();
    });

    it('does not fetch history when modal is closed', () => {
      render(<RoleHistoryModal {...defaultProps} isOpen={false} />);

      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('refetches history when modal is reopened', async () => {
      const { rerender } = render(<RoleHistoryModal {...defaultProps} isOpen={false} />);

      expect(global.fetch).not.toHaveBeenCalled();

      rerender(<RoleHistoryModal {...defaultProps} isOpen={true} />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Role Badge Colors', () => {
    it('displays correct badge colors for different roles', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        const aeBadges = screen.getAllByText('Account Executive');
        expect(aeBadges.length).toBeGreaterThan(0);
        expect(aeBadges[0]).toHaveClass('bg-blue-100');

        const seBadges = screen.getAllByText('Sales Engineer');
        expect(seBadges.length).toBeGreaterThan(0);
        expect(seBadges[0]).toHaveClass('bg-purple-100');
      });
    });

    it('displays "None" badge for null roles', async () => {
      render(<RoleHistoryModal {...defaultProps} />);

      await waitFor(() => {
        const noneBadges = screen.getAllByText('None');
        expect(noneBadges.length).toBeGreaterThan(0);
        expect(noneBadges[0]).toHaveClass('bg-gray-100');
      });
    });
  });
});
