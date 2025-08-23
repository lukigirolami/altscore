from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
from typing import Optional

# Crear la aplicación FastAPI
app = FastAPI(
    title="Phase Change Diagram API",
    description="API para calcular volúmenes específicos de líquido y vapor basado en presión",
    version="1.0.0"
)

# Modelo de respuesta
class PhaseChangeResponse(BaseModel):
    #pressure: float
    specific_volume_liquid: float
    specific_volume_vapor: float

# Constantes del modelo
X1 = 0.00105
X2 = 0.0035
X3 = 30
Y1 = 0.05
Y2 = 10
Y3 = 0.05

# Calcular pendientes y ordenadas al origen
ML = (Y2 - Y1) / (X2 - X1)
MV = (Y3 - Y2) / (X3 - X2)
AL = Y2 - (ML * X2)
AV = Y3 - (MV * X3)

@app.get("/")
async def root():
    """Endpoint de información básica"""
    return {
        "message": "Phase Change Diagram API",
        "version": "1.0.0",
        "endpoints": {
            "phase_diagram": "/phase-change-diagram?pressure=<value>",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/phase-change-diagram", response_model=PhaseChangeResponse)
async def get_phase_change_diagram(
    pressure: float = Query(
        ..., 
        description="Presión en las unidades del sistema",
        ge=0,  # Mayor o igual a 0
        example=5.0
    )
):
    """
    Calcula los volúmenes específicos de líquido y vapor basado en la presión dada.
    
    Args:
        pressure: Valor de presión (decimal)
        
    Returns:
        PhaseChangeResponse: Objeto con presión y volúmenes específicos calculados
    """
    try:
        # Calcular volúmenes específicos usando las fórmulas proporcionadas
        specific_volume_liquid = (pressure - AL) / ML
        specific_volume_vapor = (pressure - AV) / MV
        
        # Validar que los resultados sean números válidos
        if not (isinstance(specific_volume_liquid, (int, float)) and 
                isinstance(specific_volume_vapor, (int, float))):
            raise ValueError("Cálculo inválido")
            
        return PhaseChangeResponse(
            #pressure=pressure,
            specific_volume_liquid=round(specific_volume_liquid, 6),
            specific_volume_vapor=round(specific_volume_vapor, 6)
        )
        
    except ZeroDivisionError:
        raise HTTPException(
            status_code=400, 
            detail="Error de división por cero en los cálculos"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error en los cálculos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/constants")
async def get_constants():
    """Endpoint para consultar las constantes utilizadas en los cálculos"""
    return {
        "constants": {
            "x1": X1,
            "x2": X2, 
            "x3": X3,
            "y1": Y1,
            "y2": Y2,
            "y3": Y3
        },
        "calculated_parameters": {
            "ml": ML,
            "mv": MV,
            "al": AL,
            "av": AV
        }
    }

# Configuración para ejecutar el servidor
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False
    )