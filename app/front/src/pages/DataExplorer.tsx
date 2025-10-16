import { useState, useEffect, useCallback } from 'react'
import type { ReactElement } from 'react'
import DataFilters from '../components/DataFilters'
import DataCharts from '../components/DataCharts'
import type { DataVisualization, DataFilters as FilterType } from '../types/data'

const API_BASE_URL = '/api'

/**
 * DataExplorer page component providing interactive data exploration capabilities.
 * Combines filtering controls with visualization charts to explore mental health admission data.
 * 
 * @returns React element rendering the complete data exploration interface
 */
export default function DataExplorer(): ReactElement {
  const [data, setData] = useState<DataVisualization | null>(null)
  const [filters, setFilters] = useState<FilterType>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /**
   * Fetches visualization data from the API with current filters.
   * Uses an AbortController to prevent memory leaks from cancelled requests.
   */
  const fetchData = useCallback(async () => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)

    try {
      // Build query parameters from filters
      const params = new URLSearchParams()
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)
      if (filters.gender !== undefined) params.append('gender', filters.gender.toString())
      if (filters.age_min !== undefined) params.append('age_min', filters.age_min.toString())
      if (filters.age_max !== undefined) params.append('age_max', filters.age_max.toString())
      if (filters.category) params.append('category', filters.category)
      if (filters.readmission !== undefined) params.append('readmission', filters.readmission.toString())

      const url = `${API_BASE_URL}/data/visualization?${params.toString()}`
      const response = await fetch(url, { signal: controller.signal })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const visualizationData: DataVisualization = await response.json()
      setData(visualizationData)
      setError(null)
    } catch (fetchError) {
      if ((fetchError as Error).name === 'AbortError') {
        return
      }
      setError('No se pudo cargar los datos de visualización. Verifica la conexión con el backend.')
      console.error('Failed to fetch visualization data:', fetchError)
    } finally {
      setLoading(false)
    }

    return () => controller.abort()
  }, [filters])

  // Fetch data when filters change
  useEffect(() => {
    fetchData()
  }, [fetchData])

  /**
   * Handles filter changes from the DataFilters component.
   * Updates the filters state which triggers a new data fetch.
   * 
   * @param newFilters - Updated filter values
   */
  function handleFiltersChange(newFilters: FilterType) {
    setFilters(newFilters)
  }

  return (
    <div className="explorer-page">
      <div className="explorer-header">
        <h1>Exploración de datos</h1>
        <p className="explorer-subtitle">
          Filtra y visualiza los datos de admisiones de salud mental. Los gráficos se actualizan en tiempo real según
          los filtros aplicados.
        </p>
      </div>

      <div className="explorer-layout">
        {/* Filters sidebar */}
        <aside className="explorer-sidebar">
          <DataFilters filters={filters} onFiltersChange={handleFiltersChange} />
        </aside>

        {/* Main content area with charts */}
        <main className="explorer-content">
          {loading && (
            <div className="status-message">
              <div className="spinner" />
              <p>Cargando datos de visualización...</p>
            </div>
          )}

          {error && !loading && (
            <div className="status-message status--error">
              <p>{error}</p>
              <button type="button" className="btn-retry" onClick={() => fetchData()}>
                Reintentar
              </button>
            </div>
          )}

          {data && !loading && !error && (
            <>
              {data.total_records === 0 ? (
                <div className="status-message status--warning">
                  <p>No se encontraron registros con los filtros aplicados.</p>
                  <p className="hint">Intenta ajustar o limpiar los filtros para ver más datos.</p>
                </div>
              ) : (
                <DataCharts data={data} />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  )
}

