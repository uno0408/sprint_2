from fastapi import FastAPI, HTTPException, status
from schemas import (
    PressureInput,
    PressureResponse,
    PressureFinalInput,
    PressureFinalResponse
)
from services import PressureDerivedService, PressureFinalService

app = FastAPI(
    title="Pressure Performance API",
    description="API with 2 endpoints: (2A) Derived Variables and (2B) Final Output",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

derived_service = PressureDerivedService()
final_service = PressureFinalService()


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Pressure Performance API",
        "version": "1.0.0",
        "endpoints": [
            "/api/pressure-performance (2A - Derived Variables)",
            "/api/pressure-performance/final (2B - Final Output)"
        ]
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
