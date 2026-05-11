import os
import json
import re
import joblib
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'nb_classifier.pkl')

# Load model once at module level (lazy load pattern)
_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        if os.path.exists(MODEL_PATH):
            _classifier = joblib.load(MODEL_PATH)
        else:
            _classifier = None
    return _classifier


def summarize(text: str) -> list:
    """
    Takes a long text (government report / achievements paragraph).
    Returns a list of 3-4 bullet strings (actual extracted sentences).
    Uses sumy LexRank extractive summarization.
    """
    if text is None or not text:
        return ["No achievement data available"]

    text = text.strip()

    if len(text) < 50:
        return [text]  # too short to summarize

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    sentences_count = min(4, max(2, len(text.split('.')) // 3))
    summary = summarizer(parser.document, sentences_count)
    result = [str(sentence).strip() for sentence in summary if str(sentence).strip()]

    if not result:
        return [text[:200]]  # fallback

    return result


def classify_achievement(text: str) -> str:
    """
    Takes a short text snippet about an achievement.
    Returns one of: Infrastructure, Education, Healthcare,
    Women_Empowerment, Agriculture, Youth, Unknown
    Uses the trained MultinomialNB model.
    """
    if text is None or not text:
        return "Unknown"

    text = text.strip()

    if len(text) < 5:
        return "Unknown"

    clf = get_classifier()

    if clf is None:
        return "Unknown"

    try:
        prediction = clf.predict([text])
        return str(prediction[0])
    except Exception as e:
        print(f"classify_achievement error: {e}")
        return "Unknown"


def sentiment_score(headlines: list) -> dict:
    """
    Takes a list of news headline strings.
    Returns dict: {"label": "Positive"/"Neutral"/"Negative", "score": float, "breakdown": dict}
    Uses NLTK VADER.
    """
    if headlines is None or len(headlines) == 0:
        return {
            "label": "Neutral",
            "score": 0.0,
            "breakdown": {"pos": 0, "neu": 1, "neg": 0, "compound": 0}
        }

    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(h) for h in headlines]

    avg_compound = sum(s['compound'] for s in scores) / len(scores)
    avg_pos = sum(s['pos'] for s in scores) / len(scores)
    avg_neg = sum(s['neg'] for s in scores) / len(scores)
    avg_neu = sum(s['neu'] for s in scores) / len(scores)

    # Label logic
    if avg_compound >= 0.05:
        label = "Positive"
    elif avg_compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "label": label,
        "score": round(avg_compound, 4),
        "breakdown": {
            "pos": round(avg_pos, 3),
            "neu": round(avg_neu, 3),
            "neg": round(avg_neg, 3),
            "compound": round(avg_compound, 4)
        }
    }


if __name__ == '__main__':
    # Test summarize
    test_text = (
        "Built 12 anganwadi centres in the constituency. "
        "Secured Rs 45 crore for metro expansion. "
        "Launched free skill training for 2000 youth. "
        "Inaugurated new library with 10000 books. "
        "Completed water supply project for 15 villages."
    )
    print("SUMMARIZE TEST:")
    print(summarize(test_text))
    print()

    # Test classify
    print("CLASSIFY TEST:")
    print(classify_achievement("Built new school for 500 children"))
    print(classify_achievement("Inaugurated primary health centre"))
    print(classify_achievement("Laid 3km of road in ward 7"))
    print()

    # Test sentiment
    print("SENTIMENT TEST:")
    headlines = [
        "MLA praised for completing flyover ahead of schedule",
        "Locals protest against MLA over water shortage"
    ]
    print(sentiment_score(headlines))
