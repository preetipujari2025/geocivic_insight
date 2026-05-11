import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.ml_pipeline import summarize, classify_achievement, sentiment_score


def test_summarize_returns_list():
    result = summarize("Built 10 schools. Launched hospital. Completed road. Started water project. Funded 500 women.")
    assert isinstance(result, list)
    assert len(result) > 0


def test_summarize_empty_string():
    result = summarize("")
    assert isinstance(result, list)
    assert len(result) > 0  # should return fallback


def test_summarize_none():
    result = summarize(None)
    assert isinstance(result, list)


def test_summarize_returns_strings():
    result = summarize("Built schools. Launched hospital. Completed road. Started project. Funded programme.")
    for item in result:
        assert isinstance(item, str)
        assert len(item) > 0


def test_classify_returns_string():
    result = classify_achievement("Built new school for children")
    assert isinstance(result, str)
    assert len(result) > 0


def test_classify_known_categories():
    valid = {'Infrastructure', 'Education', 'Healthcare', 'Women_Empowerment', 'Agriculture', 'Youth', 'Unknown'}
    result = classify_achievement("Inaugurated new hospital")
    assert result in valid


def test_classify_empty():
    result = classify_achievement("")
    assert result == "Unknown"


def test_classify_none():
    result = classify_achievement(None)
    assert result == "Unknown"


def test_sentiment_positive():
    headlines = [
        "MLA praised for excellent work",
        "Constituency development praised by CM",
        "Award given to MLA for outstanding service"
    ]
    result = sentiment_score(headlines)
    assert result['label'] == "Positive"
    assert -1.0 <= result['score'] <= 1.0


def test_sentiment_negative():
    headlines = [
        "MLA accused of corruption",
        "Protests erupt against MLA",
        "MLA fails to deliver on promises",
        "Scandal surrounds MLA"
    ]
    result = sentiment_score(headlines)
    assert result['label'] in ["Negative", "Neutral"]  # VADER may vary


def test_sentiment_empty_list():
    result = sentiment_score([])
    assert result['label'] == "Neutral"
    assert result['score'] == 0.0


def test_sentiment_returns_all_keys():
    result = sentiment_score(["Test headline"])
    assert 'label' in result
    assert 'score' in result
    assert 'breakdown' in result
    assert 'compound' in result['breakdown']
