import pandas as pd
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
corpus_path = os.path.join(BASE_DIR, "health_corpus.csv")

def generate_bot_reply(user_input):
    """
    Simple fallback rule-based responder using health_corpus.csv.
    """
    if not os.path.exists(corpus_path):
        return "I'm still learning. Please ask about our medicines."

    df = pd.read_csv(corpus_path)
    df['Question'] = df['Question'].str.lower()
    df['Answer'] = df['Answer'].fillna("I'm not sure about that yet.")

    for _, row in df.iterrows():
        if row['Question'] in user_input:
            return row['Answer']

    return random.choice([
        "Could you please clarify your question?",
        "I’m here to help with health and medicine queries!",
        "Sorry, I don’t have data on that yet."
    ])
