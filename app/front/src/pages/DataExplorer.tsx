/**
 * DataExplorer Page - Interactive data exploration interface.
 * 
 * This page component provides comprehensive data exploration capabilities
 * by combining filtering controls with interactive visualizations.
 */

import { useState } from 'react'
import type { ReactElement } from 'react'
import DataFilters from '../components/DataFilters'
import DataCharts from '../components/DataCharts'
import { useVisualization } from '../hooks'
import type { DataFilters as FilterType } from '../types/data'

/**
 * DataExplorer page component.
 * 
 * Combines filtering controls with visualization charts to enable
 * interactive exploration of mental health admission data. Uses the
 * useVisualization hook to automatically fetch data when filters change.
 * 
 * @returns React element rendering the complete data exploration interface
 */
export default function DataExplorer(): ReactElement {
  // Manage filter state locally
  const [filters, setFilters] = useState<FilterType>({})

  // Fetch visualization data using custom hook
  // Automatically refetches when filters change
  const { data, loading, error, refetch } = useVisualization(filters)

  /**
   * Handles filter changes from the DataFilters component.
   * Updates the filters state which triggers automatic data refetch via the hook.
   * 
   * @param newFilters - Updated filter values
   */
  function handleFiltersChange(newFilters: FilterType) {
    setFilters(newFilters)
  }

  return (
    <div className="explorer-page">
      {/* Page header */}
      <div className="explorer-header">
        <h2>Exploración de datos</h2>
        <p className="explorer-subtitle">
          Filtra y visualiza los datos de admisiones de salud mental. Los gráficos se actualizan
          en tiempo real según los filtros aplicados.
        </p>
      </div>

      {/* Main explorer layout */}
      <div className="explorer-layout">
        {/* Filters sidebar */}
        <aside className="explorer-sidebar">
          <DataFilters filters={filters} onFiltersChange={handleFiltersChange} />
        </aside>

        {/* Main content area with charts */}
        <main className="explorer-content">
          {/* Loading state */}
          {loading && (
            <div className="status-message">
              <div className="spinner" />
              <p>Cargando datos de visualización...</p>
            </div>
          )}

          {/* Error state with retry button */}
          {error && !loading && (
            <div className="status-message status--error">
              <p>{error}</p>
              <button type="button" className="btn-retry" onClick={refetch}>
                Reintentar
              </button>
            </div>
          )}

          {/* Success state with data */}
          {data && !loading && !error && (
            <>
              {data.total_records === 0 ? (
                <div className="status-message status--warning">
                  <p>No se encontraron registros con los filtros aplicados.</p>
                  <p className="hint">
                    Intenta ajustar o limpiar los filtros para ver más datos.
                  </p>
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
