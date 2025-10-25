# chatbot/bots/pharmacy_bot.py
from pathlib import Path
import pandas as pd
import random
import os

# Compute project root (two levels up from this file: chatbot/bots/ -> project root)
HERE = Path(__file__).resolve().parent  # chatbot/bots
PROJECT_ROOT = HERE.parent.parent  # chatbot/

# common expected location: project root (same place as manage.py) or a data folder
# try possible locations
possible = [
    PROJECT_ROOT / "pharmacy_corpus.csv",
    PROJECT_ROOT / "health_corpus.csv",
    PROJECT_ROOT.parent / "pharmacy_corpus.csv",
    PROJECT_ROOT.parent / "health_corpus.csv",
    PROJECT_ROOT / "data" / "pharmacy_corpus.csv",
    PROJECT_ROOT / "data" / "health_corpus.csv",
]

def load_corpus(path: Path):
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        # normalize columns
        if 'question' in df.columns.str.lower():
            # make case-insensitive mapping
            df.columns = [c.strip() for c in df.columns]
        # ensure columns exist
        if 'question' in df.columns and 'answer' in df.columns:
            df = df.dropna(subset=['question'])
            df['question'] = df['question'].astype(str).str.lower()
            df['answer'] = df['answer'].fillna("I'm not sure about that yet.")
            return df[['question', 'answer']]
    except Exception:
        return None
    return None

# load whichever exists (pharmacy corpus preferred)
CORPUS_DF = None
for p in possible:
    if p and p.exists():
        CORPUS_DF = load_corpus(Path(p))
        if CORPUS_DF is not None:
            break

def generate_bot_reply(user_input: str) -> str:
    """
    Rule based responder using available corpora.
    - tries direct contains-match (question phrase in user's input)
    - falls back to canned replies
    """
    if not user_input:
        return "Please enter a question about medicines or health."

    ui = user_input.lower()

    # 1) try direct corpus lookup
    if CORPUS_DF is not None and not CORPUS_DF.empty:
        # loop through rows and match phrases contained in user input
        for _, row in CORPUS_DF.iterrows():
            q = str(row['question']).strip().lower()
            if not q:
                continue
            # if question exactly in input or input contains question phrase
            if q in ui:
                return row['answer']

    # 2) default pharmacy-specific quick responses
    default_choices = [
        "Could you please clarify your question?",
        "I’m here to help with health and medicine queries!",
        "Sorry, I don’t have data on that yet. Try asking 'list medicines' or 'price of paracetamol'.",
        "You can ask things like: 'Do you have Paracetamol?', 'List medicines', or 'What is the price of Ibuprofen?'"
    ]

    return random.choice(default_choices)
