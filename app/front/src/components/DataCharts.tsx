import type { ReactElement } from 'react'
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

// Color palette matching Brain aesthetic
const COLORS = {
  primary: '#7C3AED',
  secondary: '#A855F7',
  tertiary: '#C4B5FD',
  accent: '#60A5FA',
  success: '#34D399',
  warning: '#FBBF24',
  danger: '#F87171',
}

const CHART_COLORS = [
  COLORS.primary,
  COLORS.secondary,
  COLORS.accent,
  COLORS.tertiary,
  COLORS.success,
  COLORS.warning,
  COLORS.danger,
]

interface DataChartsProps {
  /** Visualization data containing all chart datasets */
  data: DataVisualization
}

/**
 * DataCharts component renders multiple interactive charts displaying mental health admission data.
 * Includes category distribution, time series, gender breakdown, age groups, and length of stay.
 * 
 * @param props - Component properties
 * @returns React element with multiple chart visualizations
 */
export default function DataCharts({ data }: DataChartsProps): ReactElement {
  /**
   * Custom tooltip component for displaying detailed chart information.
   * 
   * @param active - Whether tooltip is active
   * @param payload - Data payload for tooltip
   * @param label - Label for tooltip
   * @returns Tooltip element or null
   */
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="tooltip-value" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {entry.payload.percentage !== undefined && ` (${entry.payload.percentage.toFixed(1)}%)`}
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
          <span className="summary-value">{data.total_records.toLocaleString('es-ES')}</span>
        </div>
      </div>

      {/* Category distribution bar chart */}
      <div className="chart-card">
        <h3 className="chart-title">Distribución por categoría diagnóstica</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.categories} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="category" angle={-45} textAnchor="end" stroke="#E5E7EB" />
            <YAxis stroke="#E5E7EB" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.primary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Time series line chart */}
      <div className="chart-card">
        <h3 className="chart-title">Evolución temporal de admisiones</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data.time_series} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="period" stroke="#E5E7EB" />
            <YAxis stroke="#E5E7EB" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line type="monotone" dataKey="count" stroke={COLORS.accent} strokeWidth={2} name="Admisiones" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gender distribution pie chart */}
      <div className="chart-card">
        <h3 className="chart-title">Distribución por género</h3>
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={data.gender_distribution}
              dataKey="count"
              nameKey="gender"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={(entry) => `${entry.gender}: ${entry.count} (${entry.percentage.toFixed(1)}%)`}
            >
              {data.gender_distribution.map((entry, index) => (
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
        <h3 className="chart-title">Distribución por grupos de edad</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.age_groups} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="age_group" stroke="#E5E7EB" />
            <YAxis stroke="#E5E7EB" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.secondary} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stay distribution bar chart */}
      <div className="chart-card">
        <h3 className="chart-title">Distribución de duración de estancia</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.stay_distribution} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="stay_range" stroke="#E5E7EB" />
            <YAxis stroke="#E5E7EB" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="count" fill={COLORS.success} name="Admisiones" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

