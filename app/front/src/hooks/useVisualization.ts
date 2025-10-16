/**
 * useVisualization Hook - Custom hook for fetching visualization data with filters.
 * 
 * This hook encapsulates the logic for loading visualization data from the API,
 * automatically refetching when filters change, and handling loading/error states.
 */

import { useState, useEffect, useCallback } from 'react'
import { fetchVisualizationData } from '../api'
import type { DataVisualization, DataFilters } from '../types/data'

/**
 * Return type for the useVisualization hook.
 */
export interface UseVisualizationResult {
  /** Visualization data, null if not loaded yet */
  data: DataVisualization | null
  /** Loading state */
  loading: boolean
  /** Error message, null if no error */
  error: string | null
  /** Function to manually refetch data */
  refetch: () => void
}

/**
 * Custom hook for fetching and managing visualization data with filtering.
 * 
 * Automatically refetches data when filters change. Handles cleanup of
 * pending requests when filters update or component unmounts.
 * 
 * @param filters - Filter parameters for the visualization query
 * @returns Object containing visualization data, loading state, error, and refetch function
 * 
 * @example
 * ```typescript
 * function MyComponent() {
 *   const [filters, setFilters] = useState<DataFilters>({ gender: 2 })
 *   const { data, loading, error, refetch } = useVisualization(filters)
 *   
 *   if (loading) return <div>Loading charts...</div>
 *   if (error) return <div>Error: {error}</div>
 *   if (!data) return null
 *   
 *   return <Charts data={data} />
 * }
 * ```
 */
export function useVisualization(filters: DataFilters = {}): UseVisualizationResult {
  const [data, setData] = useState<DataVisualization | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  /**
   * Memoized fetch function that depends on filters and refetchTrigger.
   * Recreated only when filters or refetch trigger changes.
   */
  const fetchData = useCallback(async () => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)

    try {
      const visualizationData = await fetchVisualizationData(filters, controller.signal)
      setData(visualizationData)
      setError(null)
    } catch (fetchError) {
      // Ignore abort errors
      if ((fetchError as Error).name === 'AbortError') {
        return
      }

      const errorMessage =
        fetchError instanceof Error
          ? fetchError.message
          : 'No se pudo cargar los datos de visualización. Verifica la conexión con el backend.'

      setError(errorMessage)
      console.error('Failed to fetch visualization data:', fetchError)
    } finally {
      setLoading(false)
    }

    return () => controller.abort()
  }, [filters, refetchTrigger])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  /**
   * Manually refetch visualization data with current filters.
   * Useful for retry buttons or manual refresh actions.
   */
  function refetch() {
    setRefetchTrigger((prev) => prev + 1)
  }

  return {
    data,
    loading,
    error,
    refetch,
  }
}

