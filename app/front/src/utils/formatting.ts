/**
 * Formatting Utilities - Helper functions for data formatting.
 * 
 * This module provides utilities for formatting numbers, dates, and other
 * data types for display in the UI.
 */

/**
 * Formats a number using Spanish locale (thousands separator).
 * 
 * @param value - The number to format
 * @returns Formatted string with Spanish locale
 * 
 * @example
 * ```typescript
 * formatNumber(1234567) // "1.234.567"
 * ```
 */
export function formatNumber(value: number): string {
  return value.toLocaleString('es-ES')
}

/**
 * Formats a date string into a localized Spanish date/time.
 * 
 * @param dateString - ISO date string
 * @returns Formatted date/time string
 * 
 * @example
 * ```typescript
 * formatDateTime('2025-10-16T10:30:00Z') // "16/10/2025, 10:30:00"
 * ```
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('es-ES')
}

/**
 * Formats a date string into a short localized Spanish date.
 * 
 * @param dateString - ISO date string
 * @returns Formatted date string
 * 
 * @example
 * ```typescript
 * formatDate('2025-10-16') // "16/10/2025"
 * ```
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES')
}

/**
 * Formats a percentage value with Spanish locale.
 * 
 * @param value - Percentage value (0-100)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string
 * 
 * @example
 * ```typescript
 * formatPercentage(45.678) // "45,7%"
 * formatPercentage(45.678, 2) // "45,68%"
 * ```
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals).replace('.', ',')}%`
}

/**
 * Truncates text to a maximum length with ellipsis.
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 * 
 * @example
 * ```typescript
 * truncateText('Lorem ipsum dolor sit amet', 15) // "Lorem ipsum..."
 * ```
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text
  }
  return `${text.slice(0, maxLength)}...`
}

