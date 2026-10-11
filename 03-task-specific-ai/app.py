
from transformers import pipeline

# Load a pretrained model for sentiment classification
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device=-1,  # Run on CPU
)

texts = [
    "I love learning artificial intelligence.",
    "This application is frustrating and useless.",
    "The package arrived this morning.",
]

results = classifier(texts)

for text, result in zip(texts, results):
    print(f"\nText: {text}")
    print(f"Predicted label: {result['label']}")
    print(f"Model score: {result['score']:.4f}")
