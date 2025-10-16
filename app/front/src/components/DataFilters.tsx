import { useState, useEffect } from 'react'
import type { ReactElement } from 'react'
import type { DataFilters } from '../types/data'

interface DataFiltersProps {
  /** Callback function invoked when filters change */
  onFiltersChange: (filters: DataFilters) => void
  /** Current filter values */
  filters: DataFilters
}

/**
 * DataFilters component provides UI controls for filtering mental health admission data.
 * Supports filtering by date range, gender, age range, diagnostic category, and readmission status.
 * 
 * @param props - Component properties
 * @returns React element rendering the filter controls
 */
export default function DataFilters({ onFiltersChange, filters }: DataFiltersProps): ReactElement {
  const [categories, setCategories] = useState<string[]>([])
  const [loadingCategories, setLoadingCategories] = useState(true)

  // Fetch available categories on component mount
  useEffect(() => {
    async function fetchCategories() {
      try {
        const response = await fetch('/api/data/categories')
        if (response.ok) {
          const data = await response.json()
          setCategories(data.categories || [])
        }
      } catch (error) {
        console.error('Failed to fetch categories:', error)
      } finally {
        setLoadingCategories(false)
      }
    }

    fetchCategories()
  }, [])

  /**
   * Handles changes to individual filter fields.
   * Updates the filters object and triggers the parent callback.
   * 
   * @param field - The filter field being updated
   * @param value - The new value for the field
   */
  function handleFilterChange(field: keyof DataFilters, value: string | number | boolean | undefined) {
    const newFilters = { ...filters, [field]: value }
    onFiltersChange(newFilters)
  }

  /**
   * Resets all filters to their default empty state.
   */
  function handleReset() {
    onFiltersChange({})
  }

  return (
    <div className="filters-panel">
      <div className="filters-header">
        <h3>Filtros de datos</h3>
        <button type="button" className="btn-reset" onClick={handleReset}>
          Limpiar filtros
        </button>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-start-date">Fecha inicio</label>
        <input
          id="filter-start-date"
          type="date"
          className="filter-input"
          value={filters.start_date || ''}
          onChange={(e) => handleFilterChange('start_date', e.target.value || undefined)}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-end-date">Fecha fin</label>
        <input
          id="filter-end-date"
          type="date"
          className="filter-input"
          value={filters.end_date || ''}
          onChange={(e) => handleFilterChange('end_date', e.target.value || undefined)}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-gender">Género</label>
        <select
          id="filter-gender"
          className="filter-input"
          value={filters.gender?.toString() || ''}
          onChange={(e) => handleFilterChange('gender', e.target.value ? parseInt(e.target.value) : undefined)}
        >
          <option value="">Todos</option>
          <option value="1">Hombre</option>
          <option value="2">Mujer</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-age-min">Edad mínima</label>
        <input
          id="filter-age-min"
          type="number"
          className="filter-input"
          placeholder="Edad mínima"
          value={filters.age_min || ''}
          onChange={(e) => handleFilterChange('age_min', e.target.value ? parseInt(e.target.value) : undefined)}
          min="0"
          max="120"
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-age-max">Edad máxima</label>
        <input
          id="filter-age-max"
          type="number"
          className="filter-input"
          placeholder="Edad máxima"
          value={filters.age_max || ''}
          onChange={(e) => handleFilterChange('age_max', e.target.value ? parseInt(e.target.value) : undefined)}
          min="0"
          max="120"
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-category">Categoría diagnóstica</label>
        <select
          id="filter-category"
          className="filter-input"
          value={filters.category || ''}
          onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
          disabled={loadingCategories}
        >
          <option value="">Todas las categorías</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-readmission">Estado de reingreso</label>
        <select
          id="filter-readmission"
          className="filter-input"
          value={filters.readmission === undefined ? '' : filters.readmission.toString()}
          onChange={(e) =>
            handleFilterChange('readmission', e.target.value === '' ? undefined : e.target.value === 'true')
          }
        >
          <option value="">Todos</option>
          <option value="true">Solo reingresos</option>
          <option value="false">Sin reingreso</option>
        </select>
      </div>
    </div>
  )
}

