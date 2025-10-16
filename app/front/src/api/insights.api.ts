/**
 * Insights API Service - Handles all insights-related API calls.
 * 
 * This service encapsulates communication with the insights microservice,
 * providing a clean interface for fetching analytical insights.
 */

import { get } from './client'
import type { InsightSummary } from '../types/insights'

/**
 * Fetches analytical insights summary from the backend.
 * 
 * This method retrieves aggregated metrics and highlights for the
 * Brain dashboard, including admission statistics, demographic data,
 * and risk factors.
 * 
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise resolving to insight summary data
 * @throws {APIError} If the request fails
 * 
 * @example
 * ```typescript
 * const controller = new AbortController()
 * const insights = await fetchInsights(controller.signal)
 * console.log(insights.highlight_phrases)
 * ```
 */
export async function fetchInsights(signal?: AbortSignal): Promise<InsightSummary> {
  return get<InsightSummary>('/insights', undefined, signal)
}

