# sentiment_classification.py
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F

# Load the pre-trained FinBERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
model.eval()

# Function to classify sentiment
def classify_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = F.softmax(outputs.logits, dim=1)
        confidence, predicted_class = torch.max(probabilities, dim=1)

    # Define sentiment labels
    sentiment_labels = ["positive", "negative", "neutral"]
    return sentiment_labels[int(predicted_class.item())], confidence.item()

# Example usage
text = "The stock market is performing well today."
sentiment, confidence = classify_sentiment(text)
print(f"Sentiment: {sentiment}, Confidence: {confidence:.2f}")