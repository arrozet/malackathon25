/**
 * useCategories Hook - Custom hook for fetching diagnostic categories.
 * 
 * This hook encapsulates the logic for loading available diagnostic categories
 * from the API, typically used to populate filter dropdowns.
 */

import { useState, useEffect } from 'react'
import { fetchCategories, type CategoriesResponse } from '../api'

/**
 * Return type for the useCategories hook.
 */
export interface UseCategoriesResult {
  /** Array of category names */
  categories: string[]
  /** Total count of categories */
  total: number
  /** Loading state */
  loading: boolean
  /** Error message, null if no error */
  error: string | null
  /** Function to manually refetch categories */
  refetch: () => void
}

/**
 * Custom hook for fetching and managing diagnostic categories.
 * 
 * Automatically fetches categories on mount and handles cleanup on unmount.
 * Provides loading, error states, and manual refetch capability.
 * 
 * @returns Object containing categories array, total count, loading state, error, and refetch function
 * 
 * @example
 * ```typescript
 * function CategoryFilter() {
 *   const { categories, loading, error } = useCategories()
 *   
 *   if (loading) return <div>Loading categories...</div>
 *   if (error) return <div>Error: {error}</div>
 *   
 *   return (
 *     <select>
 *       {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
 *     </select>
 *   )
 * }
 * ```
 */
export function useCategories(): UseCategoriesResult {
  const [categoriesData, setCategoriesData] = useState<CategoriesResponse>({
    categories: [],
    total: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadCategories() {
      setLoading(true)
      setError(null)

      try {
        const data = await fetchCategories(controller.signal)
        setCategoriesData(data)
        setError(null)
      } catch (fetchError) {
        // Ignore abort errors
        if ((fetchError as Error).name === 'AbortError') {
          return
        }

        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : 'No se pudieron cargar las categorías. Verifica la conexión con el backend.'

        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    loadCategories()

    // Cleanup: abort ongoing request on unmount
    return () => controller.abort()
  }, [refetchTrigger])

  /**
   * Manually refetch categories data.
   * Useful for retry buttons or manual refresh actions.
   */
  function refetch() {
    setRefetchTrigger((prev) => prev + 1)
  }

  return {
    categories: categoriesData.categories,
    total: categoriesData.total,
    loading,
    error,
    refetch,
  }
}

