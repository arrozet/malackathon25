"""
Pydantic data models for the FastAPI backend.

These schemas describe the structure of the insight responses served by the
prototype backend while the real Oracle database integration is prepared.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class InsightMetric(BaseModel):
    """Metric describing a single highlighted figure for the dashboard."""

    title: str = Field(..., description="Short human-readable metric title.")
    value: str = Field(..., description="Formatted value ready for display.")
    description: str = Field(
        ..., description="Context explaining why the metric matters."
    )


class InsightSection(BaseModel):
    """Logical group of metrics that share a common research angle."""

    title: str = Field(..., description="Section title shown in the UI.")
    metrics: List[InsightMetric] = Field(
        ..., description="Collection of related metrics for the section."
    )


class InsightSummary(BaseModel):
    """Summary payload presented to the Brain frontend prototype."""

    generated_at: datetime = Field(
        ..., description="UTC timestamp when the summary was produced."
    )
    sample_period: str = Field(
        ..., description="Human-readable description of the temporal scope."
    )
    highlight_phrases: List[str] = Field(
        ..., description="Key takeaways emphasised in the landing page hero."
    )
    metric_sections: List[InsightSection] = Field(
        ..., description="Breakdown of metrics grouped by theme.")
    database_connected: bool = Field(
        ..., description="Whether the Oracle datasource is reachable."
    )


class DataFilters(BaseModel):
    """Filter parameters for data exploration queries."""
    
    start_date: str | None = Field(None, description="Start date for filtering (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="End date for filtering (YYYY-MM-DD)")
    gender: int | None = Field(None, description="Gender filter (1=male, 2=female)")
    age_min: int | None = Field(None, description="Minimum age filter")
    age_max: int | None = Field(None, description="Maximum age filter")
    category: str | None = Field(None, description="Diagnostic category filter")
    readmission: bool | None = Field(None, description="Filter by readmission status")


class CategoryDistribution(BaseModel):
    """Distribution of admissions by diagnostic category."""
    
    category: str = Field(..., description="Diagnostic category name")
    count: int = Field(..., description="Number of admissions")
    percentage: float = Field(..., description="Percentage of total")


class AgeDistribution(BaseModel):
    """Distribution of admissions by age group."""
    
    age_group: str = Field(..., description="Age group label")
    count: int = Field(..., description="Number of admissions")
    percentage: float = Field(..., description="Percentage of total")


class TimeSeriesData(BaseModel):
    """Time series data point for admissions over time."""
    
    period: str = Field(..., description="Time period label (YYYY-MM)")
    count: int = Field(..., description="Number of admissions in period")


class GenderDistribution(BaseModel):
    """Distribution of admissions by gender."""
    
    gender: str = Field(..., description="Gender label")
    count: int = Field(..., description="Number of admissions")
    percentage: float = Field(..., description="Percentage of total")


class StayDistribution(BaseModel):
    """Distribution of length of stay."""
    
    stay_range: str = Field(..., description="Stay duration range")
    count: int = Field(..., description="Number of admissions")
    percentage: float = Field(..., description="Percentage of total")


class DataVisualization(BaseModel):
    """Complete data visualization payload with multiple chart data."""
    
    total_records: int = Field(..., description="Total records matching filters")
    categories: List[CategoryDistribution] = Field(..., description="Category distribution")
    age_groups: List[AgeDistribution] = Field(..., description="Age group distribution")
    time_series: List[TimeSeriesData] = Field(..., description="Admissions over time")
    gender_distribution: List[GenderDistribution] = Field(..., description="Gender distribution")
    stay_distribution: List[StayDistribution] = Field(..., description="Length of stay distribution")
    filters_applied: DataFilters = Field(..., description="Filters used for this visualization")



