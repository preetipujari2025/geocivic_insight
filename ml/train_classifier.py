import pandas as pd
import numpy as np
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'training_data', 'achievements.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)


def train():
    """Train the achievement text classifier and save the model."""
    # Load training data
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} training samples")
    print(df['category'].value_counts())

    # Prepare features and labels
    X = df['text'].values
    y = df['category'].values

    # Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create pipeline with TF-IDF vectorizer and Naive Bayes classifier
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), max_features=5000, stop_words='english')),
        ('classifier', MultinomialNB(alpha=0.1))
    ])

    # Train the model
    pipeline.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest accuracy: {accuracy:.2%}")
    print(classification_report(y_test, y_pred))

    # Save the trained model
    joblib.dump(pipeline, os.path.join(MODEL_DIR, 'nb_classifier.pkl'))
    print(f"Model saved to {MODEL_DIR}/nb_classifier.pkl")

    return pipeline


if __name__ == '__main__':
    train()
