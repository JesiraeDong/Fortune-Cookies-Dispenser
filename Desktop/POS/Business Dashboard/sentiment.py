import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
client = OpenAI(
    api_key="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"
)

def analyze_sentiment(text):
    """Analyze sentiment of text using OpenAI's GPT-3.5-turbo model."""
    try:
        prompt = f"""Analyze the sentiment of this restaurant feedback. Consider food quality, taste, service, and overall experience.
        Respond with EXACTLY one word: 'Positive', 'Neutral', or 'Negative'.
        
        Guidelines:
        - Complaints about food quality (too salty, undercooked, overcooked) are Negative
        - Service issues are Negative
        - Price complaints are Negative
        - Mixed feedback with both positive and negative points is Neutral
        - Only clearly positive experiences are Positive
        
        Feedback: {text}
        
        Sentiment:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a restaurant feedback analyzer that responds with exactly one word."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        sentiment = response.choices[0].message.content.strip()
        
        # Ensure we only return valid sentiment values
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            return "Neutral"
        
        return sentiment
            
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        # Enhanced fallback: check for restaurant-specific keywords
        text = text.lower()
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'delicious', 'wonderful', 'fantastic',
            'love', 'best', 'fresh', 'tasty', 'perfect', 'friendly', 'attentive', 'quick',
            'recommend', 'enjoyed', 'clean', 'authentic', 'favorite'
        ]
        negative_words = [
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst', 'disappointed',
            'not good', 'slow', 'cold', 'undercooked', 'overcooked', 'salty', 'bland',
            'rude', 'dirty', 'expensive', 'wait', 'wrong', 'missing', 'late', 'mess',
            'dry', 'tough', 'tasteless', 'mediocre', 'waste', 'never again'
        ]
        
        # Convert text to words for more accurate matching
        words = text.split()
        
        # Count positive and negative matches
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        # Check for negations (e.g., "not good", "wasn't great")
        negations = ['not', 'no', 'never', "wasn't", "weren't", "isn't", "aren't", "hadn't", "doesn't"]
        for i, word in enumerate(words[:-1]):
            if word in negations:
                # If next word is positive, count it as negative instead
                if any(pos_word in words[i+1] for pos_word in positive_words):
                    pos_count -= 1
                    neg_count += 1
        
        if pos_count > neg_count:
            return "Positive"
        elif neg_count > pos_count:
            return "Negative"
        return "Neutral" 