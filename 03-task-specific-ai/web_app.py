
import gradio as gr
from transformers import pipeline

MODEL_ID = (
    "distilbert/"
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# Load the model once when the server starts.
classifier = pipeline(
    "sentiment-analysis",
    model=MODEL_ID,
    device=-1,
)


def predict_sentiment(text):
    if not text or not text.strip():
        return {"Error": 1.0}

    result = classifier(text.strip())[0]

    return {
        result["label"]: round(result["score"], 4)
    }


demo = gr.Interface(
    fn=predict_sentiment,
    inputs=gr.Textbox(
        label="Enter a sentence",
        placeholder="I love learning AI!",
        lines=3,
    ),
    outputs=gr.Label(label="Prediction"),
    title="Positive or Negative Sentence Finder",
    description=(
        "Enter an English sentence to predict "
        "whether its sentiment is positive or negative."
    ),
)

if __name__ == "__main__":
    demo.launch()
