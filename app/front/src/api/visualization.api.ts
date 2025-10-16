/**
 * Visualization API Service - Handles data visualization API calls.
 * 
 * This service encapsulates communication with the visualization microservice,
 * providing methods for fetching filtered and aggregated visualization data.
 */

import { get } from './client'
import type { DataVisualization, DataFilters } from '../types/data'

/**
 * Fetches visualization data with optional filters.
 * 
 * This method retrieves aggregated data for multiple chart types including
 * category distributions, time series, age groups, gender distribution,
 * and length of stay data. All filters are optional.
 * 
 * @param filters - Optional filter parameters
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise resolving to visualization data
 * @throws {APIError} If the request fails
 * 
 * @example
 * ```typescript
 * const filters = {
 *   gender: 2,
 *   age_min: 18,
 *   age_max: 29
 * }
 * const data = await fetchVisualizationData(filters)
 * console.log(data.total_records)
 * ```
 */
export async function fetchVisualizationData(
  filters?: DataFilters,
  signal?: AbortSignal
): Promise<DataVisualization> {
  const params = filters
    ? {
        start_date: filters.start_date,
        end_date: filters.end_date,
        gender: filters.gender,
        age_min: filters.age_min,
        age_max: filters.age_max,
        category: filters.category,
        readmission: filters.readmission,
      }
    : undefined

  return get<DataVisualization>('/data/visualization', params, signal)
}

