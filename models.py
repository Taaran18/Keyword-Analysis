from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer


def load_question_classifier():
    tokenizer = AutoTokenizer.from_pretrained("mrsinghania/asr-question-detection")
    model = AutoModelForSequenceClassification.from_pretrained(
        "mrsinghania/asr-question-detection"
    )
    return pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)


def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")
