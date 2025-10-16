/**
 * Data types for visualization and filtering.
 * These types match the Pydantic models from the FastAPI backend.
 */

export interface DataFilters {
  start_date?: string
  end_date?: string
  gender?: number
  age_min?: number
  age_max?: number
  category?: string
  readmission?: boolean
}

export interface CategoryDistribution {
  category: string
  count: number
  percentage: number
}

export interface AgeDistribution {
  age_group: string
  count: number
  percentage: number
}

export interface TimeSeriesData {
  period: string
  count: number
}

export interface GenderDistribution {
  gender: string
  count: number
  percentage: number
}

export interface StayDistribution {
  stay_range: string
  count: number
  percentage: number
}

export interface DataVisualization {
  total_records: number
  categories: CategoryDistribution[]
  age_groups: AgeDistribution[]
  time_series: TimeSeriesData[]
  gender_distribution: GenderDistribution[]
  stay_distribution: StayDistribution[]
  filters_applied: DataFilters
}

