"""
Mock ML Pipeline for testing purposes.

This file provides mock implementations of ML functions
to avoid ML dependencies during testing and development.
"""

def summarize(text):
    """
    Mock summarization function.
    
    Args:
        text (str): Input text to summarize
        
    Returns:
        str: Mock summary
    """
    if not text:
        return "No achievements data available."
    
    # Simple mock summarization
    sentences = text.split('. ')
    if len(sentences) > 2:
        return '. '.join(sentences[:2]) + '.'
    return text


def classify_achievement(text):
    """
    Mock achievement classification function.
    
    Args:
        text (str): Achievement text to classify
        
    Returns:
        list: List of achievement categories
    """
    if not text:
        return []
    
    # Simple mock classification based on keywords
    categories = []
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['school', 'education', 'college']):
        categories.append('Education')
    if any(keyword in text_lower for keyword in ['hospital', 'health', 'medical']):
        categories.append('Healthcare')
    if any(keyword in text_lower for keyword in ['road', 'highway', 'bridge']):
        categories.append('Infrastructure')
    if any(keyword in text_lower for keyword in ['training', 'youth', 'skill']):
        categories.append('Youth Development')
    
    return categories if categories else ['General Development']


def sentiment_score(text):
    """
    Mock sentiment analysis function.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Mock sentiment result with 'label' and 'score' keys
    """
    if not text:
        return {'label': 'Neutral', 'score': 0.0}
    
    # Simple mock sentiment based on keywords
    text_lower = text.lower()
    positive_words = ['built', 'completed', 'launched', 'improved', 'successful']
    negative_words = ['failed', 'delayed', 'cancelled', 'problem', 'issue']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return {'label': 'Positive', 'score': 0.5}
    elif negative_count > positive_count:
        return {'label': 'Negative', 'score': -0.5}
    else:
        return {'label': 'Neutral', 'score': 0.0}