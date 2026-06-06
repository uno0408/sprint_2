from pydantic import BaseModel, Field


# ========================
# API 2A - Input Schema (Derived Variables)
# ========================
class PressureInput(BaseModel):
    """Primary input for API 2A: batting innings with match context."""
    innings: list[dict] = Field(
        ..., 
        description="List of innings with match context",
        min_items=1,
        max_items=100
    )


# ========================
# API 2A - Output Schema (Derived Variables)
# ========================
class PressureResponse(BaseModel):
    """Output for API 2A: 4 derived variables."""
    pressure_indicator: bool = Field(..., description="Whether pressure situations identified")
    pressure_runs: int = Field(..., description="Total runs in pressure innings")
    pressure_balls: int = Field(..., description="Total balls in pressure innings")
    pressure_strike_rate: float = Field(..., description="Strike rate in pressure")
    baseline_strike_rate: float = Field(..., description="Baseline strike rate")
    pressure_sample_size: int = Field(..., description="Number of pressure innings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pressure_indicator": True,
                "pressure_runs": 187,
                "pressure_balls": 156,
                "pressure_strike_rate": 119.87,
                "baseline_strike_rate": 95.42,
                "pressure_sample_size": 4
            }
        }


# ========================
# API 2B - Input Schema (Final Output)
# ========================
class PressureFinalInput(BaseModel):
    """Primary input for API 2B: derived variables from API 2A."""
    pressure_indicator: bool = Field(..., description="Whether pressure situations identified")
    pressure_runs: int = Field(..., ge=0, description="Total runs in pressure innings")
    pressure_balls: int = Field(..., ge=0, description="Total balls in pressure innings")
    pressure_strike_rate: float = Field(..., ge=0, description="Strike rate in pressure")
    baseline_strike_rate: float = Field(..., ge=0, description="Baseline strike rate")
    pressure_sample_size: int = Field(..., ge=0, description="Number of pressure innings")


# ========================
# API 2B - Output Schema (Final Output)
# ========================
class PressureFinalResponse(BaseModel):
    """Output for API 2B: Final score + label + explanation."""
    pressure_performance_score: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Final Pressure Performance Score (0-100)"
    )
    pressure_label: str = Field(..., description="Elite/Strong/Average/Weak")
    baseline_comparison: dict = Field(..., description="Context-aware comparison")
    derived_variables_used: list[str] = Field(..., description="List of variables used")
    explanation: str = Field(..., description="Contextual explanation")
    pressure_strike_rate_out: float = Field(..., description="Pressure strike rate")
    baseline_strike_rate_out: float = Field(..., description="Baseline strike rate")
    pressure_sample_size_out: int = Field(..., description="Number of pressure innings")
    pressure_runs_out: int = Field(..., description="Total pressure runs")
    pressure_balls_out: int = Field(..., description="Total pressure balls")
    formula_used: str = Field(..., description="Formula used")
    threshold_breakdown: str = Field(..., description="Label thresholds")
    context_awareness_note: str = Field(..., description="Context-aware explanation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pressure_performance_score": 78.45,
                "pressure_label": "Strong",
                "baseline_comparison": {
                    "direction": "better_than_baseline",
                    "difference": 24.45,
                    "percentage": 25.58
                },
                "derived_variables_used": ["pressure_strike_rate", "baseline_strike_rate", "pressure_sample_size"],
                "explanation": "Pressure Performance Score of 78.45 indicates Strong pressure performance.",
                "pressure_strike_rate_out": 119.87,
                "baseline_strike_rate_out": 95.42,
                "pressure_sample_size_out": 4,
                "pressure_runs_out": 187,
                "pressure_balls_out": 156,
                "formula_used": "PPS = ((pressure_SR / baseline_SR) × 0.6 + (pressure_sample_size / 10) × 0.4) × 100",
                "threshold_breakdown": "Elite: ≥85 | Strong: 70-84 | Average: 55-69 | Weak: <55",
                "context_awareness_note": "Score is context-aware because it uses pressure_SR/baseline_SR ratio + sample_size."
            }
        }
