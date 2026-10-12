from fastapi.middleware.cors import CORSMiddleware
import json
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from workers import asgi

SPACE_ID = os.getenv("HF_SPACE_ID", "vineel6/sentiment-finder")
SPACE_URL = f"https://{SPACE_ID.replace('/', '-')}.hf.space"
PREDICT_URL = (
    f"{SPACE_URL}/gradio_api/call/predict_sentiment"
)

app = FastAPI(title="Sentiment Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
	"https://sentiment-finder-web.pages.dev"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class PredictionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class PredictionResponse(BaseModel):
    label: str
    score: float


@app.get("/")
async def home():
    return {"message": "Sentiment Analysis API is running on Cloudflare"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=422,
            detail="Please provide non-empty text.",
        )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            submission = await client.post(
                PREDICT_URL,
                json={"data": [text]},
            )
            submission.raise_for_status()
            event_id = submission.json()["event_id"]

            result_response = await client.get(
                f"{PREDICT_URL}/{event_id}",
            )
            result_response.raise_for_status()

        result = None
        current_event = None
        data_lines = []

        for line in result_response.text.splitlines():
            if line.startswith("event:"):
                current_event = line[6:].strip()
                data_lines = []
            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())

                if current_event == "complete":
                    result = json.loads("\n".join(data_lines))
                    break

        if not result or not isinstance(result, list):
            raise ValueError("No completed prediction was returned.")

        prediction = result[0]
        label = prediction["label"]
        confidences = prediction.get("confidences", [])

        matching = next(
            (item for item in confidences if item["label"] == label),
            None,
        )
        score = float(matching["confidence"]) if matching else 0.0

        return PredictionResponse(label=label, score=score)

    except HTTPException:
        raise
    except Exception as exc:
        # Keep implementation details in server logs, not API responses.
        print(f"Prediction request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The hosted sentiment model could not return a prediction.",
        ) from exc


Default = asgi.entrypoint(app)

