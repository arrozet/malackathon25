/**
 * Categories API Service - Handles diagnostic category API calls.
 * 
 * This service encapsulates communication with the categories microservice,
 * providing methods for fetching available diagnostic categories.
 */

import { get } from './client'

/**
 * Response type for categories endpoint.
 */
export interface CategoriesResponse {
  /** Array of diagnostic category names */
  categories: string[]
  /** Total count of categories */
  total: number
}

/**
 * Fetches all available diagnostic categories.
 * 
 * This method retrieves the list of unique diagnostic categories
 * available in the dataset. Useful for populating filter dropdowns
 * and category selectors.
 * 
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise resolving to categories data
 * @throws {APIError} If the request fails
 * 
 * @example
 * ```typescript
 * const { categories, total } = await fetchCategories()
 * console.log(`Found ${total} categories:`, categories)
 * ```
 */
export async function fetchCategories(signal?: AbortSignal): Promise<CategoriesResponse> {
  return get<CategoriesResponse>('/data/categories', undefined, signal)
}

