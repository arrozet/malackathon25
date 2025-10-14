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



