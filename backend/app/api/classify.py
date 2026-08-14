from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.classifier import sky_classifier
from app.services.explain import explain_service

router = APIRouter(prefix="/api", tags=["classify"])


class ClassifyRequest(BaseModel):
    u: float = Field(..., gt=0, le=40, description="Kecerahan filter ultraviolet")
    g: float = Field(..., gt=0, le=40, description="Kecerahan filter hijau")
    r: float = Field(..., gt=0, le=40, description="Kecerahan filter merah")
    i: float = Field(..., gt=0, le=40, description="Kecerahan filter inframerah dekat")
    z: float = Field(..., gt=0, le=40, description="Kecerahan filter inframerah")


class ClassifyResponse(BaseModel):
    predicted_class: str
    label: str
    confidence: float
    probabilities: dict[str, float]
    color_index: dict[str, float]

class ExplainResponse(ClassifyResponse):
    explanation: str


@router.post("/classify/explain", response_model=ExplainResponse)
def classify_with_explanation(request: ClassifyRequest) -> ExplainResponse:
    try:
        result = explain_service.explain(
            u=request.u, g=request.g, r=request.r, i=request.i, z=request.z
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Gagal membuat penjelasan: {error}")

    return ExplainResponse(**result)


@router.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    try:
        result = sky_classifier.predict(
            u=request.u, g=request.g, r=request.r, i=request.i, z=request.z
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan klasifikasi: {error}")

    return ClassifyResponse(**result)