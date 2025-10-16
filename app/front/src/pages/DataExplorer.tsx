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
      {/* 
        ACCESIBILIDAD: <h1> como título principal de la página.
        Cada vista debe tener un único h1 que identifique el contenido principal.
        REFERENCIA: WCAG 2.1 - 2.4.6 Headings and Labels (Level AA)
      */}
      <header className="explorer-header">
        <h1>Exploración de datos</h1>
        <p className="explorer-subtitle">
          Filtra y visualiza los datos de admisiones de salud mental. Los gráficos se actualizan
          en tiempo real según los filtros aplicados.
        </p>
      </header>

      {/* Main explorer layout */}
      <div className="explorer-layout">
        {/* 
          ACCESIBILIDAD: <aside> sin role redundante.
          El elemento <aside> ya tiene semántica implícita de complementary.
          REFERENCIA: WCAG 2.1 - 4.1.2 Name, Role, Value (Level A)
        */}
        <aside className="explorer-sidebar" aria-label="Panel de filtros de datos">
          <DataFilters filters={filters} onFiltersChange={handleFiltersChange} />
        </aside>

        {/* 
          ACCESIBILIDAD: Uso de <div> en lugar de <main>.
          Solo debe haber un único <main> por página (definido en App.tsx).
          REFERENCIA: HTML5 Spec - The main element
        */}
        <div className="explorer-content" aria-label="Área de visualización de datos">
          {/* Loading state */}
          {loading && (
            <div className="status-message" role="status" aria-live="polite" aria-busy="true">
              <div className="spinner" aria-hidden="true" />
              <p>Cargando datos de visualización...</p>
            </div>
          )}

          {/* Error state with retry button */}
          {error && !loading && (
            <div className="status-message status--error" role="alert" aria-live="assertive">
              <p>{error}</p>
              <button 
                type="button" 
                className="btn-retry" 
                onClick={refetch}
                aria-label="Reintentar carga de datos"
              >
                Reintentar
              </button>
            </div>
          )}

          {/* Success state with data */}
          {data && !loading && !error && (
            <>
              {data.total_records === 0 ? (
                <div className="status-message status--warning" role="status" aria-live="polite">
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
        </div>
      </div>
    </div>
  )
}
