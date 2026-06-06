from typing import List
from schemas import PressureInput, PressureFinalInput


class PressureDerivedService:
    """Service for API 2A: Calculate derived variables from raw innings."""
    
    def is_pressure_situation(self, inning: dict) -> bool:
        """Check if inning is pressure situation."""
        wickets_lost = inning.get("wickets_lost", 0)
        balls_remaining = inning.get("balls_remaining", 0)
        match_phase = inning.get("match_phase", "")
        
        # Pressure: chasing + late phase + wickets falling
        if match_phase in ["late", "crisis"]:
            return wickets_lost >= 5 and balls_remaining <= 15
        return False
    
    def compute_derived_variables(self, inputs: PressureInput):
        """API 2A: Compute 4 derived variables."""
        innings = inputs.innings
        
        pressure_runs = 0
        pressure_balls = 0
        pressure_innings = []
        
        for inning in innings:
            if self.is_pressure_situation(inning):
                pressure_runs += inning.get("runs_scored", 0)
                pressure_balls += inning.get("balls_faced", 0)
                pressure_innings.append(inning)
        
        pressure_sample_size = len(pressure_innings)
        pressure_indicator = pressure_sample_size > 0
        
        # pressure_strike_rate
        pressure_strike_rate = (pressure_runs / pressure_balls * 100) if pressure_balls > 0 else 0.0
        
        # baseline_strike_rate (all innings)
        total_runs = sum(inning.get("runs_scored", 0) for inning in innings)
        total_balls = sum(inning.get("balls_faced", 0) for inning in innings)
        baseline_strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0.0
        
        return {
            "pressure_indicator": pressure_indicator,
            "pressure_runs": pressure_runs,
            "pressure_balls": pressure_balls,
            "pressure_strike_rate": round(pressure_strike_rate, 2),
            "baseline_strike_rate": round(baseline_strike_rate, 2),
            "pressure_sample_size": pressure_sample_size
        }


class PressureFinalService:
    """Service for API 2B: Calculate final score from derived variables."""
    
    @staticmethod
    def calculate_pps(pressure_sr: float, baseline_sr: float, sample_size: int) -> tuple:
        """API 2B: Calculate PPS formula (context-aware)."""
        if sample_size < 2 or baseline_sr == 0:
            return 0.0, 0.0, 0.0
        
        ratio = pressure_sr / baseline_sr
        pps = (ratio * 0.6 + (sample_size / 10) * 0.4) * 100
        return round(min(100, pps), 2), round(ratio, 4), round((ratio - 1) * 100, 2)
    
    @staticmethod
    def get_pressure_label(pps: float) -> str:
        """API 2B: Get label based on PPS threshold."""
        if pps >= 85:
            return "Elite"
        elif pps >= 70:
            return "Strong"
        elif pps >= 55:
            return "Average"
        else:
            return "Weak"
    
    async def get_pressure_performance_final(self, inputs: PressureFinalInput):
        """API 2B: Main method to produce final output."""
        # Calculate PPS
        pps, ratio, percentage_diff = self.calculate_pps(
            inputs.pressure_strike_rate,
            inputs.baseline_strike_rate,
            inputs.pressure_sample_size
        )
        
        # Get label
        label = self.get_pressure_label(pps)
        
        # Baseline comparison
        direction = "better_than_baseline" if ratio > 1.0 else "worse_than_baseline" if ratio < 1.0 else "equal"
        baseline_comparison = {
            "direction": direction,
            "difference": round(inputs.pressure_strike_rate - inputs.baseline_strike_rate, 2),
            "percentage": round(percentage_diff, 2)
        }
        
        return {
            "pressure_performance_score": pps,
            "pressure_label": label,
            "baseline_comparison": baseline_comparison,
            "derived_variables_used": ["pressure_strike_rate", "baseline_strike_rate", "pressure_sample_size", "pressure_runs", "pressure_balls"],
            "explanation": f"Pressure Performance Score of {pps} indicates {label} pressure performance level. Player scored {percentage_diff:.1f}% {direction.replace('_', ' ')} under pressure with pressure strike rate of {inputs.pressure_strike_rate} vs baseline strike rate of {inputs.baseline_strike_rate}, based on {inputs.pressure_sample_size} pressure innings.",
            "pressure_strike_rate_out": inputs.pressure_strike_rate,
            "baseline_strike_rate_out": inputs.baseline_strike_rate,
            "pressure_sample_size_out": inputs.pressure_sample_size,
            "pressure_runs_out": inputs.pressure_runs,
            "pressure_balls_out": inputs.pressure_balls,
            "formula_used": "PPS = ((pressure_SR / baseline_SR) × 0.6 + (pressure_sample_size / 10) × 0.4) × 100 if sample_size ≥ 2, else 0",
            "threshold_breakdown": "Elite: ≥85 | Strong: 70-84 | Average: 55-69 | Weak: <55",
            "context_awareness_note": "Score is context-aware because it uses pressure_strike_rate/baseline_strike_rate ratio (accounts for match context) + pressure_sample_size (accounts for reliability), NOT just raw runs."
        }
    


# ========================
# API 2A - Derived Variables Endpoint
# ========================
@app.post(
    "/api/pressure-performance",
    response_model=PressureResponse,
    tags=["Pressure Performance 2A - Derived Variables"]
)
async def get_pressure_performance_derived(inputs: PressureInput):
    """
    API 2A: Convert raw innings into derived variables for Pressure Performance.
    
    **4 Required Output Fields:**
    - pressure_indicator: Whether pressure situations identified
    - pressure_runs: Total runs in pressure innings
    - pressure_balls: Total balls in pressure innings
    - pressure_strike_rate: Strike rate in pressure
    """
    try:
        result = derived_service.compute_derived_variables(inputs)
        return PressureResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to compute pressure derived variables", "details": str(e)}
        )


# ========================
# API 2B - Final Output Endpoint
# ========================
@app.post(
    "/api/pressure-performance/final",
    response_model=PressureFinalResponse,
    tags=["Pressure Performance 2B - Final Output"]
)
async def get_pressure_performance_final(inputs: PressureFinalInput):
    """
    API 2B: Produce final Pressure Performance score from derived variables.
    
    **5 Required Output Fields:**
    - pressure_performance_score: Final score (0-100)
    - pressure_label: Elite/Strong/Average/Weak
    - baseline_comparison: Context-aware comparison
    - derived_variables_used: List of variables used
    - explanation: Contextual explanation
    """
    try:
        result = await final_service.get_pressure_performance_final(inputs)
        return PressureFinalResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to compute Pressure Performance Score", "details": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
