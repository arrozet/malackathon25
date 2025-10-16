/**
 * useInsights Hook - Custom hook for fetching insights data.
 * 
 * This hook encapsulates the logic for loading insights from the API,
 * including loading states, error handling, and automatic cleanup.
 */

import { useState, useEffect } from 'react'
import { fetchInsights } from '../api'
import type { InsightSummary } from '../types/insights'

/**
 * Return type for the useInsights hook.
 */
export interface UseInsightsResult {
  /** Insights data, null if not loaded yet */
  insights: InsightSummary | null
  /** Loading state */
  loading: boolean
  /** Error message, null if no error */
  error: string | null
  /** Function to manually refetch insights */
  refetch: () => void
}

/**
 * Custom hook for fetching and managing insights data.
 * 
 * Automatically fetches insights on mount and handles cleanup on unmount.
 * Provides loading, error states, and manual refetch capability.
 * 
 * @returns Object containing insights data, loading state, error, and refetch function
 * 
 * @example
 * ```typescript
 * function MyComponent() {
 *   const { insights, loading, error, refetch } = useInsights()
 *   
 *   if (loading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error}</div>
 *   if (!insights) return null
 *   
 *   return <div>{insights.highlight_phrases.join(', ')}</div>
 * }
 * ```
 */
export function useInsights(): UseInsightsResult {
  const [insights, setInsights] = useState<InsightSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadInsights() {
      setLoading(true)
      setError(null)

      try {
        const data = await fetchInsights(controller.signal)
        setInsights(data)
        setError(null)
      } catch (fetchError) {
        // Ignore abort errors
        if ((fetchError as Error).name === 'AbortError') {
          return
        }

        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : 'No se pudo conectar con el backend. Verifica que el servicio esté activo.'

        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    loadInsights()

    // Cleanup: abort ongoing request on unmount
    return () => controller.abort()
  }, [refetchTrigger])

  /**
   * Manually refetch insights data.
   * Useful for retry buttons or manual refresh actions.
   */
  function refetch() {
    setRefetchTrigger((prev) => prev + 1)
  }

  return {
    insights,
    loading,
    error,
    refetch,
  }
}

