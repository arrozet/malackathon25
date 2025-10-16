/**
 * HTTP Client - Base client for all API communications.
 * 
 * This module provides a centralized HTTP client with consistent error handling,
 * request/response interceptors, and configuration management.
 */

/**
 * API configuration containing base URL and default headers.
 */
export const API_CONFIG = {
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
}

/**
 * Custom error class for API-related errors.
 * Extends the base Error class with HTTP status information.
 */
export class APIError extends Error {
  /**
   * Creates an API error instance.
   * 
   * @param message - Error message
   * @param status - HTTP status code
   * @param statusText - HTTP status text
   */
  constructor(
    message: string,
    public status?: number,
    public statusText?: string
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Performs a GET request to the specified endpoint.
 * 
 * @param endpoint - API endpoint path (relative to baseURL)
 * @param params - Optional query parameters
 * @param signal - Optional AbortSignal for cancellation
 * @returns Promise resolving to the response data
 * @throws {APIError} If the request fails
 */
export async function get<T>(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined>,
  signal?: AbortSignal
): Promise<T> {
  // Build query string from params
  const queryString = params
    ? '?' + new URLSearchParams(
        Object.entries(params)
          .filter(([, value]) => value !== undefined)
          .map(([key, value]) => [key, String(value)])
      ).toString()
    : ''

  const url = `${API_CONFIG.baseURL}${endpoint}${queryString}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: API_CONFIG.headers,
      signal,
    })

    if (!response.ok) {
      throw new APIError(
        `API request failed: ${response.statusText}`,
        response.status,
        response.statusText
      )
    }

    const data: T = await response.json()
    return data
  } catch (error) {
    // Re-throw abort errors as-is
    if (error instanceof Error && error.name === 'AbortError') {
      throw error
    }

    // Wrap other errors in APIError
    if (error instanceof APIError) {
      throw error
    }

    throw new APIError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      undefined,
      undefined
    )
  }
}

/**
 * Performs a POST request to the specified endpoint.
 * 
 * @param endpoint - API endpoint path (relative to baseURL)
 * @param body - Request body data
 * @param signal - Optional AbortSignal for cancellation
 * @returns Promise resolving to the response data
 * @throws {APIError} If the request fails
 */
export async function post<T, B = unknown>(
  endpoint: string,
  body: B,
  signal?: AbortSignal
): Promise<T> {
  const url = `${API_CONFIG.baseURL}${endpoint}`

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: API_CONFIG.headers,
      body: JSON.stringify(body),
      signal,
    })

    if (!response.ok) {
      throw new APIError(
        `API request failed: ${response.statusText}`,
        response.status,
        response.statusText
      )
    }

    const data: T = await response.json()
    return data
  } catch (error) {
    // Re-throw abort errors as-is
    if (error instanceof Error && error.name === 'AbortError') {
      throw error
    }

    // Wrap other errors in APIError
    if (error instanceof APIError) {
      throw error
    }

    throw new APIError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      undefined,
      undefined
    )
  }
}

