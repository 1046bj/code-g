"""
Code-G API request/response schemas.
"""
from typing import Optional

from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    """Company context for better funding match."""

    industry: Optional[str] = Field(None, description="e.g. AI/Vision, Bio/Health, SaaS, Manufacturing")
    year_established: Optional[int] = Field(None, ge=1900, le=2100, description="Year established, e.g. 2018")
    revenue_krw: Optional[int] = Field(None, ge=0, description="Revenue last year in KRW")
    employees: Optional[int] = Field(None, ge=0, description="Number of employees")
    focus: Optional[str] = Field(None, description="R&D Focus or Commercialization/Sales Focus")
    keywords: list[str] = Field(default_factory=list, description="e.g. Vision, Unmanned, Smart Farm")


class AnalyzeRequest(BaseModel):
    """Request body for /api/code-g/analyze and /api/code-g/deep-analyze."""

    url: str = Field(..., description="Funding notice URL to crawl and analyze")
    profile: Optional[CompanyProfile] = Field(None, description="Company profile for context")
