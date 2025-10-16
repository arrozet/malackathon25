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

      {/* 
        ACCESIBILIDAD: Gráfico con role="img" y descripción detallada.
        Se usa h3 para mantener jerarquía correcta (h1 > h2 > h3).
        Se incluye aria-describedby para descripción accesible extendida.
        REFERENCIA: WCAG 2.1 - 1.1.1 Non-text Content (Level A)
      */}
      <div 
        className="chart-card" 
        role="img" 
        aria-labelledby="chart-categories-title"
        aria-describedby="chart-categories-desc"
      >
        <h3 className="chart-title" id="chart-categories-title">Distribución por categoría diagnóstica</h3>
        <p id="chart-categories-desc" className="sr-only">
          Gráfico de barras horizontal mostrando la distribución de {data.total_records} admisiones 
          clasificadas en {data.categories.length} categorías diagnósticas diferentes. Cada barra 
          representa el número total de admisiones para esa categoría específica.
        </p>
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

      {/* ACCESIBILIDAD: Gráfico de evolución temporal con descripción semántica */}
      <div 
        className="chart-card" 
        role="img" 
        aria-labelledby="chart-timeseries-title"
        aria-describedby="chart-timeseries-desc"
      >
        <h3 className="chart-title" id="chart-timeseries-title">Evolución temporal de admisiones</h3>
        <p id="chart-timeseries-desc" className="sr-only">
          Gráfico de líneas que muestra la evolución temporal del número de admisiones a lo largo de 
          {data.time_series.length} períodos de tiempo. Permite identificar tendencias y patrones 
          estacionales en las admisiones hospitalarias de salud mental.
        </p>
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

      {/* ACCESIBILIDAD: Gráfico circular con patrones para daltonismo */}
      <div 
        className="chart-card" 
        role="img" 
        aria-labelledby="chart-gender-title"
        aria-describedby="chart-gender-desc"
      >
        <h3 className="chart-title" id="chart-gender-title">Distribución por género</h3>
        <p id="chart-gender-desc" className="sr-only">
          Gráfico circular mostrando la distribución de admisiones por género: 
          {data.gender_distribution.map(g => `${g.gender} representa ${g.percentage.toFixed(1)}% con ${g.count} admisiones`).join(', ')}. 
          Los sectores usan patrones visuales (líneas y puntos) además de colores para facilitar 
          la distinción a personas con daltonismo.
        </p>
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

      {/* ACCESIBILIDAD: Gráfico de distribución etaria */}
      <div 
        className="chart-card" 
        role="img" 
        aria-labelledby="chart-age-title"
        aria-describedby="chart-age-desc"
      >
        <h3 className="chart-title" id="chart-age-title">Distribución por grupos de edad</h3>
        <p id="chart-age-desc" className="sr-only">
          Gráfico de barras verticales mostrando la distribución de admisiones clasificadas en 
          {data.age_groups.length} grupos de edad diferentes. Permite identificar qué rangos etarios 
          tienen mayor incidencia de admisiones hospitalarias en salud mental.
        </p>
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

      {/* ACCESIBILIDAD: Gráfico de duración de estancia */}
      <div 
        className="chart-card" 
        role="img" 
        aria-labelledby="chart-stay-title"
        aria-describedby="chart-stay-desc"
      >
        <h3 className="chart-title" id="chart-stay-title">Distribución de duración de estancia</h3>
        <p id="chart-stay-desc" className="sr-only">
          Gráfico de barras mostrando la distribución de la duración de estancia hospitalaria clasificada 
          en {data.stay_distribution.length} rangos diferentes. Ayuda a identificar la duración típica de 
          las hospitalizaciones y detectar estancias prolongadas que puedan requerir atención especial.
        </p>
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
