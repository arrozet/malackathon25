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
   * 
   * @param props - Tooltip properties
   * @returns Tooltip element or null
   */
  const CustomTooltip = (props: any) => {
    const { active, payload, label } = props
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="tooltip-value" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {entry.payload.percentage !== undefined &&
                ` (${entry.payload.percentage.toFixed(1)}%)`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="charts-container">
      {/* Summary statistics */}
      <div className="chart-summary">
        <div className="summary-card">
          <span className="summary-label">Total de registros</span>
          <span className="summary-value">{formatNumber(data.total_records)}</span>
        </div>
      </div>

      {/* Category distribution bar chart */}
      <div className="chart-card">
        <h4 className="chart-title">Distribución por categoría diagnóstica</h4>
        <ResponsiveContainer width="100%" height={isMobile ? 600 : 500}>
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
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.primary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Time series line chart */}
      <div className="chart-card">
        <h4 className="chart-title">Evolución temporal de admisiones</h4>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={data.time_series}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="period" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke={COLORS.accent}
              strokeWidth={2}
              name="Admisiones"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gender distribution pie chart */}
      <div className="chart-card">
        <h4 className="chart-title">Distribución por género</h4>
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
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
              {data.gender_distribution.map((_, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Age distribution bar chart */}
      <div className="chart-card">
        <h4 className="chart-title">Distribución por grupos de edad</h4>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.age_groups} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="age_group" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.secondary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stay distribution bar chart */}
      <div className="chart-card">
        <h4 className="chart-title">Distribución de duración de estancia</h4>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={data.stay_distribution}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="stay_range" stroke={COLORS.text} />
            <YAxis stroke={COLORS.text} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.success} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
