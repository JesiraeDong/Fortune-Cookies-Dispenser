import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_sentiment(text):
    """
    Analyze the sentiment of given text using OpenAI's GPT-3.5-turbo.
    Returns: "Positive", "Neutral", or "Negative"
    """
    try:
        # First try using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a sentiment analyzer for restaurant feedback. 
                Analyze the sentiment based on:
                - Food quality and taste
                - Service quality
                - Overall experience
                
                Guidelines:
                - Positive: Excellent food, great service, wonderful experience, highly recommended
                - Neutral: Okay food, decent service, acceptable experience
                - Negative: Poor food quality, bad service, complaints about taste, temperature, or preparation
                
                Examples:
                - "Food was delicious and service was great" -> Positive
                - "The food was okay but service was slow" -> Neutral
                - "Food was too salty and service was terrible" -> Negative
                
                Respond with ONLY one word: Positive, Neutral, or Negative."""},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=10
        )
        
        sentiment = response.choices[0].message.content.strip().lower()
        
        # Validate the response
        if sentiment in ['positive', 'neutral', 'negative']:
            return sentiment.capitalize()
            
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
    
    # Fallback to keyword-based analysis if OpenAI fails
    positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'delicious', 'perfect', 'love', 'enjoy', 'fantastic', 'best', 'outstanding', 'favorite', 'recommend', 'awesome', 'tasty', 'yummy', 'satisfied', 'happy', 'pleased', 'impressed', 'exceeded', 'excellent', 'perfect', 'outstanding', 'amazing', 'wonderful', 'fantastic', 'great', 'good', 'delicious', 'tasty', 'yummy', 'love', 'enjoy', 'recommend', 'satisfied', 'happy', 'pleased', 'impressed'}
    negative_words = {'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing', 'worst', 'hate', 'dislike', 'unpleasant', 'unsatisfactory', 'mediocre', 'average', 'okay', 'fine', 'meh', 'not good', 'could be better', 'salty', 'undercooked', 'overcooked', 'cold', 'spicy', 'bland', 'dry', 'tough', 'chewy', 'soggy', 'burnt', 'raw', 'frozen', 'expired', 'old', 'stale', 'rotten', 'moldy', 'unfresh', 'unclean', 'dirty', 'unsanitary', 'slow', 'unfriendly', 'rude', 'impolite', 'unprofessional', 'inattentive', 'ignored', 'forgotten', 'wrong order', 'mistake', 'error', 'problem', 'issue', 'complaint', 'disappointed', 'frustrated', 'angry', 'upset', 'unhappy', 'dissatisfied', 'unpleasant', 'unsatisfactory', 'mediocre', 'average', 'okay', 'fine', 'meh', 'not good', 'could be better'}
    
    text = text.lower()
    
    # Check for negations
    negations = {'not', "n't", 'no', 'never', 'none', 'neither', 'nor'}
    words = text.split()
    
    positive_count = 0
    negative_count = 0
    
    for i, word in enumerate(words):
        # Check if the word is a negation
        is_negated = any(neg in words[max(0, i-2):i] for neg in negations)
        
        if word in positive_words:
            positive_count += -1 if is_negated else 1
        elif word in negative_words:
            negative_count += -1 if is_negated else 1
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral" 