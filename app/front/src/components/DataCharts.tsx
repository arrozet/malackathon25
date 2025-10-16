/**
 * DataCharts Component - Interactive chart visualizations.
 * 
 * This component renders multiple interactive charts displaying mental health
 * admission data including category distributions, time series, gender breakdown,
 * age groups, and length of stay.
 */

import { type ReactElement, useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { DataVisualization } from '../types/data'
import { COLORS, CHART_COLORS } from '../utils/constants'
import { formatNumber } from '../utils/formatting'

/**
 * Props for the DataCharts component.
 */
interface DataChartsProps {
  /** Visualization data containing all chart datasets */
  data: DataVisualization
}

/**
 * DataCharts component renders interactive visualizations.
 * 
 * Displays multiple chart types using the Recharts library with
 * consistent styling from the Brain design system. Includes custom
 * tooltips for enhanced data display.
 * 
 * @param props - Component properties
 * @returns React element with multiple chart visualizations
 */
export default function DataCharts({ data }: DataChartsProps): ReactElement {
  /**
   * Hook to detect if the screen is mobile-sized.
   * Updates on window resize to ensure responsive behavior.
   */
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    // Check on mount
    checkMobile()
    
    // Add resize listener
    window.addEventListener('resize', checkMobile)
    
    // Cleanup
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  /**
   * Custom tooltip component for displaying detailed chart information.
   * Ensures WCAG AA compliance with 4.5:1 contrast ratio for all text.
   * 
   * @param props - Tooltip properties
   * @returns Tooltip element or null
   */
  const CustomTooltip = (props: any) => {
    const { active, payload, label } = props
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip" role="tooltip" aria-live="polite">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="tooltip-value">
              <span className="tooltip-indicator" style={{ backgroundColor: entry.color }} aria-hidden="true" />
              <span className="tooltip-text">
                {entry.name}: <strong>{entry.value}</strong>
                {entry.payload.percentage !== undefined &&
                  ` (${entry.payload.percentage.toFixed(1)}%)`}
              </span>
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  /**
   * Custom cursor styling configuration.
   * Uses a vibrant purple line that's clearly visible.
   */
  const customCursor = {
    stroke: COLORS.secondary,
    strokeWidth: 3,
    opacity: 0.9,
    strokeDasharray: '5 5',
  }

  /**
   * Custom bar cursor styling.
   * Creates a visible purple overlay on hover.
   */
  const customBarCursor = {
    fill: COLORS.secondary,
    opacity: 0.3,
  }

  return (
    <div className="charts-container" role="region" aria-label="Visualizaciones de datos de admisiones">
      {/* Summary statistics */}
      <div className="chart-summary" role="status" aria-live="polite">
        <div className="summary-card">
          <span className="summary-label">Total de registros</span>
          <span className="summary-value" aria-label={`${formatNumber(data.total_records)} registros en total`}>
            {formatNumber(data.total_records)}
          </span>
        </div>
      </div>

      {/* Category distribution bar chart */}
      <div className="chart-card" role="img" aria-label={`Gráfico de barras mostrando distribución de admisiones por categoría diagnóstica. Total de ${data.categories.length} categorías representadas.`}>
        <h4 className="chart-title" id="chart-categories-title">Distribución por categoría diagnóstica</h4>
        <ResponsiveContainer width="100%" height={isMobile ? 600 : 500} aria-labelledby="chart-categories-title">
          <BarChart 
            data={data.categories} 
            layout="vertical"
            margin={isMobile 
              ? { top: 20, right: 10, left: 10, bottom: 20 }
              : { top: 20, right: 30, left: 20, bottom: 20 }
            }
          >
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis type="number" stroke={COLORS.text} />
            <YAxis 
              type="category" 
              dataKey="category" 
              stroke={COLORS.text}
              width={isMobile ? 120 : 260}
              style={{ fontSize: isMobile ? '10px' : '13px' }}
              tick={{ width: isMobile ? 120 : 260 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={customBarCursor} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.primary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Time series line chart */}
      <div className="chart-card" role="img" aria-label={`Gráfico de líneas mostrando la evolución temporal de admisiones. Presenta ${data.time_series.length} períodos de tiempo.`}>
        <h4 className="chart-title" id="chart-timeseries-title">Evolución temporal de admisiones</h4>
        <ResponsiveContainer width="100%" height={400} aria-labelledby="chart-timeseries-title">
          <LineChart
            data={data.time_series}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="period" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} cursor={customCursor} />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke={COLORS.accent}
              strokeWidth={2}
              name="Admisiones"
              dot={{ fill: COLORS.accent, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: COLORS.primary, stroke: COLORS.accent, strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gender distribution pie chart */}
      <div className="chart-card" role="img" aria-label={`Gráfico circular mostrando distribución por género. ${data.gender_distribution.map(g => `${g.gender}: ${g.percentage.toFixed(1)}%`).join(', ')}`}>
        <h4 className="chart-title" id="chart-gender-title">Distribución por género</h4>
        <ResponsiveContainer width="100%" height={400} aria-labelledby="chart-gender-title">
          <PieChart>
            {/* SVG pattern definitions for accessibility - allows color-blind users to distinguish sectors */}
            <defs>
              {/* Diagonal lines pattern - creates a background with base color and white diagonal lines */}
              {CHART_COLORS.map((color, idx) => (
                <pattern
                  key={`pattern-diagonal-${idx}`}
                  id={`pattern-diagonal-${idx}`}
                  width="10"
                  height="10"
                  patternUnits="userSpaceOnUse"
                  patternTransform="rotate(45)"
                >
                  <rect width="10" height="10" fill={color} />
                  <line x1="0" y1="0" x2="0" y2="10" stroke="#FFFFFF" strokeWidth="3" opacity="0.5" />
                </pattern>
              ))}
              {/* Dots pattern - creates a background with base color and white dots */}
              {CHART_COLORS.map((color, idx) => (
                <pattern
                  key={`pattern-dots-${idx}`}
                  id={`pattern-dots-${idx}`}
                  width="12"
                  height="12"
                  patternUnits="userSpaceOnUse"
                >
                  <rect width="12" height="12" fill={color} />
                  <circle cx="6" cy="6" r="2" fill="#FFFFFF" opacity="0.6" />
                </pattern>
              ))}
              {/* Horizontal lines pattern - creates a background with base color and white horizontal lines */}
              {CHART_COLORS.map((color, idx) => (
                <pattern
                  key={`pattern-horizontal-${idx}`}
                  id={`pattern-horizontal-${idx}`}
                  width="10"
                  height="10"
                  patternUnits="userSpaceOnUse"
                >
                  <rect width="10" height="10" fill={color} />
                  <line x1="0" y1="5" x2="10" y2="5" stroke="#FFFFFF" strokeWidth="3" opacity="0.5" />
                </pattern>
              ))}
            </defs>
            <Pie
              data={data.gender_distribution as any[]}
              dataKey="count"
              nameKey="gender"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={(entry: any) =>
                `${entry.gender}: ${entry.count} (${entry.percentage.toFixed(1)}%)`
              }
            >
              {data.gender_distribution.map((_, index) => {
                // Define pattern types for each sector: diagonal, dots, or horizontal
                const patternTypes = ['diagonal', 'dots', 'horizontal']
                const patternType = patternTypes[index % patternTypes.length]
                const colorIndex = index % CHART_COLORS.length
                
                // Use pattern fill instead of solid color for accessibility
                return (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={`url(#pattern-${patternType}-${colorIndex})`}
                  />
                )
              })}
            </Pie>
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Age distribution bar chart */}
      <div className="chart-card" role="img" aria-label={`Gráfico de barras mostrando distribución por grupos de edad. Total de ${data.age_groups.length} grupos etarios.`}>
        <h4 className="chart-title" id="chart-age-title">Distribución por grupos de edad</h4>
        <ResponsiveContainer width="100%" height={400} aria-labelledby="chart-age-title">
          <BarChart data={data.age_groups} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="age_group" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} cursor={customBarCursor} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.secondary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stay distribution bar chart */}
      <div className="chart-card" role="img" aria-label={`Gráfico de barras mostrando distribución de duración de estancia hospitalaria. Total de ${data.stay_distribution.length} rangos de duración.`}>
        <h4 className="chart-title" id="chart-stay-title">Distribución de duración de estancia</h4>
        <ResponsiveContainer width="100%" height={400} aria-labelledby="chart-stay-title">
          <BarChart
            data={data.stay_distribution}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="stay_range" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} cursor={customBarCursor} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.success} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
