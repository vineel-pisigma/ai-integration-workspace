
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

# 1. Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

# 2. Load the trained classification model
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
model.eval()

text = "I love learning artificial intelligence."

# 3. Convert text into numerical inputs
inputs = tokenizer(text, return_tensors="pt")

print("Original text:", text)
print("Token IDs:", inputs["input_ids"].tolist())
print("Tokens:", tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]))

# 4. Run inference without calculating gradients
with torch.no_grad():
    outputs = model(**inputs)

# 5. Inspect the raw model scores
logits = outputs.logits
probabilities = torch.softmax(logits, dim=-1)

print("\nRaw logits:", logits.tolist())
print("Probabilities:", probabilities.tolist())

# 6. Convert the highest-scoring class into a label
predicted_id = probabilities.argmax(dim=-1).item()
predicted_label = model.config.id2label[predicted_id]

print("Predicted label:", predicted_label)
