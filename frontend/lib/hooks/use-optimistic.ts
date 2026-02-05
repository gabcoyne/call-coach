/**
 * Optimistic UI Update Utilities
 *
 * Provides hooks and utilities for optimistic UI updates with SWR.
 * Allows updating UI immediately before server confirmation for better UX.
 */

import { useState, useCallback } from "react";
import { useSWRConfig } from "swr";

/**
 * Options for optimistic updates
 */
export interface OptimisticUpdateOptions<T> {
  /**
   * Function to generate optimistic data before server response
   */
  optimisticData: (currentData: T | undefined) => T;

  /**
   * Function to rollback if the mutation fails
   */
  rollback?: (currentData: T | undefined) => T;

  /**
   * Whether to revalidate after the mutation succeeds
   */
  revalidate?: boolean;

  /**
   * Whether to show a loading state during optimistic update
   */
  populateCache?: boolean;
}

/**
 * Hook for managing optimistic updates with SWR
 *
 * @example
 * ```tsx
 * function UpdateScoreButton({ callId, newScore }: Props) {
 *   const { data, mutate } = useCallAnalysis(callId);
 *   const { performOptimisticUpdate, isOptimistic } = useOptimistic();
 *
 *   const handleUpdate = async () => {
 *     await performOptimisticUpdate(
 *       `/api/coaching/analyze-call?call_id=${callId}`,
 *       async () => {
 *         const response = await fetch('/api/coaching/update-score', {
 *           method: 'POST',
 *           body: JSON.stringify({ callId, newScore }),
 *         });
 *         return response.json();
 *       },
 *       {
 *         optimisticData: (current) => ({
 *           ...current!,
 *           scores: { ...current!.scores, overall: newScore },
 *         }),
 *         rollback: (current) => current!,
 *       }
 *     );
 *   };
 *
 *   return (
 *     <button onClick={handleUpdate} disabled={isOptimistic}>
 *       Update Score {isOptimistic && '(saving...)'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useOptimistic() {
  const { mutate } = useSWRConfig();
  const [isOptimistic, setIsOptimistic] = useState(false);

  const performOptimisticUpdate = useCallback(
    async <T,>(
      key: string | string[],
      updateFn: () => Promise<T>,
      options: OptimisticUpdateOptions<T>
    ): Promise<T> => {
      const {
        optimisticData,
        rollback,
        revalidate = true,
        populateCache = true,
      } = options;

      setIsOptimistic(true);

      try {
        // Perform optimistic update
        const result = await mutate<T>(
          key,
          async (currentData) => {
            // Apply optimistic data immediately
            if (populateCache) {
              mutate(key, optimisticData(currentData), false);
            }

            // Perform the actual update
            const newData = await updateFn();

            return newData;
          },
          {
            optimisticData: optimisticData as any,
            rollbackOnError: true,
            populateCache,
            revalidate,
          }
        );

        setIsOptimistic(false);
        return result as T;
      } catch (error) {
        // Rollback on error if provided
        if (rollback) {
          await mutate(key, (currentData: T | undefined) => rollback(currentData), false);
        }

        setIsOptimistic(false);
        throw error;
      }
    },
    [mutate]
  );

  return {
    performOptimisticUpdate,
    isOptimistic,
  };
}

/**
 * Hook for managing list mutations with optimistic updates
 * Useful for adding/removing items from a list
 *
 * @example
 * ```tsx
 * function CallList() {
 *   const { data } = useSearchCalls(filters);
 *   const { addItem, removeItem } = useOptimisticList();
 *
 *   const handleAddBookmark = async (callId: string) => {
 *     await addItem(
 *       '/api/coaching/search-calls',
 *       async () => {
 *         await fetch('/api/bookmarks', {
 *           method: 'POST',
 *           body: JSON.stringify({ callId }),
 *         });
 *         return { call_id: callId, title: 'New Call', ... };
 *       },
 *       (current, newItem) => [newItem, ...(current || [])]
 *     );
 *   };
 *
 *   return <div>{data?.map((call) => <CallCard key={call.call_id} call={call} />)}</div>;
 * }
 * ```
 */
export function useOptimisticList<T>() {
  const { mutate } = useSWRConfig();

  const addItem = useCallback(
    async (
      key: string | string[],
      updateFn: () => Promise<T>,
      optimisticDataFn: (current: T[] | undefined, newItem: T) => T[]
    ): Promise<T> => {
      const newItem = await updateFn();

      await mutate<T[]>(
        key,
        (currentData) => optimisticDataFn(currentData, newItem),
        {
          revalidate: false,
          populateCache: true,
        }
      );

      return newItem;
    },
    [mutate]
  );

  const removeItem = useCallback(
    async (
      key: string | string[],
      predicate: (item: T) => boolean,
      updateFn: () => Promise<void>
    ): Promise<void> => {
      // Apply optimistic update
      await mutate<T[]>(
        key,
        (currentData) => currentData?.filter((item) => !predicate(item)),
        { revalidate: false, populateCache: true }
      );

      try {
        // Perform the actual update
        await updateFn();
      } catch (error) {
        // Revalidate on error to restore the list
        await mutate(key);
        throw error;
      }
    },
    [mutate]
  );

  const updateItem = useCallback(
    async (
      key: string | string[],
      predicate: (item: T) => boolean,
      updateFn: () => Promise<T>
    ): Promise<T> => {
      const updatedItem = await updateFn();

      await mutate<T[]>(
        key,
        (currentData) =>
          currentData?.map((item) =>
            predicate(item) ? updatedItem : item
          ),
        {
          revalidate: false,
          populateCache: true,
        }
      );

      return updatedItem;
    },
    [mutate]
  );

  return {
    addItem,
    removeItem,
    updateItem,
  };
}

/**
 * Hook for managing a single item mutation with optimistic updates
 *
 * @example
 * ```tsx
 * function CallAnalysisActions({ callId }: Props) {
 *   const { data } = useCallAnalysis(callId);
 *   const { updateItem } = useOptimisticItem();
 *
 *   const handleAddNote = async (note: string) => {
 *     await updateItem(
 *       `/api/coaching/analyze-call?call_id=${callId}`,
 *       async () => {
 *         const response = await fetch('/api/coaching/add-note', {
 *           method: 'POST',
 *           body: JSON.stringify({ callId, note }),
 *         });
 *         return response.json();
 *       },
 *       (current) => ({
 *         ...current!,
 *         action_items: [...current!.action_items, note],
 *       })
 *     );
 *   };
 *
 *   return <button onClick={() => handleAddNote('Follow up')}>Add Note</button>;
 * }
 * ```
 */
export function useOptimisticItem<T>() {
  const { mutate } = useSWRConfig();

  const updateItem = useCallback(
    async (
      key: string | string[],
      updateFn: () => Promise<T>,
      optimisticDataFn: (current: T | undefined) => T
    ): Promise<T> => {
      // Apply optimistic update
      await mutate<T>(key, optimisticDataFn, { revalidate: false, populateCache: true });

      try {
        // Perform the actual update
        const updatedItem = await updateFn();

        // Update with server response
        await mutate<T>(key, updatedItem, { revalidate: false, populateCache: true });

        return updatedItem;
      } catch (error) {
        // Revalidate on error to restore the original data
        await mutate(key);
        throw error;
      }
    },
    [mutate]
  );

  return {
    updateItem,
  };
}
