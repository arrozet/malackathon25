/**
 * Application Constants - Centralized configuration values.
 * 
 * This module contains all constant values used throughout the application
 * including navigation items, color palettes, and configuration settings.
 */

/**
 * Navigation items for the main menu.
 */
export const NAV_ITEMS = [
  { id: 'vision', label: 'Visión general' },
  { id: 'insights', label: 'Insights clave' },
  { id: 'explorer', label: 'Exploración de datos' },
] as const

/**
 * Brain color palette matching the design system.
 * Based on purple theme with dark background (#0D0C1D).
 */
export const COLORS = {
  /** Primary purple for main actions and brand (#7C3AED) */
  primary: '#7C3AED',
  /** Secondary lighter purple (#A855F7) */
  secondary: '#A855F7',
  /** Tertiary lightest purple (#C4B5FD) */
  tertiary: '#C4B5FD',
  /** Accent blue for highlights (#60A5FA) */
  accent: '#60A5FA',
  /** Success green (#34D399) */
  success: '#34D399',
  /** Warning yellow (#FBBF24) */
  warning: '#FBBF24',
  /** Danger red (#F87171) */
  danger: '#F87171',
  /** Background dark (#0D0C1D) */
  background: '#0D0C1D',
  /** Text off-white (#E5E7EB) */
  text: '#E5E7EB',
  /** Border gray (#374151) */
  border: '#374151',
  /** Secondary content gray (#4B5563) */
  muted: '#4B5563',
} as const

/**
 * Chart color palette derived from the main color scheme.
 * Used for consistent coloring across all visualizations.
 */
export const CHART_COLORS = [
  COLORS.primary,
  COLORS.secondary,
  COLORS.accent,
  COLORS.tertiary,
  COLORS.success,
  COLORS.warning,
  COLORS.danger,
] as const

/**
 * Application metadata.
 */
export const APP_META = {
  name: 'Brain',
  tagline: 'tu compañera de investigación',
  description: 'Investigación clínica',
  hackathon: 'Malackathon 2025',
} as const

