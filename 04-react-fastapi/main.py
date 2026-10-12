
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from gradio_client import Client, handle_file

SPACE_ID = os.getenv(
    "HF_SPACE_ID",
    "vineel6/sentiment-finder",
)

app = FastAPI(title="Sentiment Analysis API")

# During local development, allow the Vite frontend.
# We will restrict this origin appropriately for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class PredictionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

class PredictionResponse(BaseModel):
    label: str
    score: float

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Please provide a non-empty sentence.",
        )

    try:
        client = Client(SPACE_ID)
        
        result = client.predict(
            text,
            api_name="/predict_sentiment",
        )

        if isinstance(result, dict):
            # Gradio Label may return label + confidences.
            label = result.get("label")
            confidences = result.get("confidences") or []

            if label is not None and confidences:
                matching = next(
                    (
                        item for item in confidences
                        if item.get("label") == label
                    ),
                    None,
                )
                score = (
                    float(matching["confidence"])
                    if matching and matching.get("confidence") is not None
                    else 0.0
                )
            elif label is not None:
                score = 0.0
            else:
                # Also support a simple {label: score} dictionary.
                label = max(result, key=result.get)
                score = float(result[label])
        else:
            raise ValueError(
                f"Unexpected model response: {type(result).__name__}"
            )

        return PredictionResponse(
            label=str(label),
            score=score,
        )


    except Exception as exc:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail=f"Hosted model call failed: {type(exc).__name__}: {exc}",
        ) from exc
