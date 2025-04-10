import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
client = OpenAI(
    api_key="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"
)

def analyze_sentiment(text):
    """Analyze sentiment of text using OpenAI's GPT-3.5-turbo model with enhanced context awareness."""
    try:
        prompt = f"""Analyze the sentiment of this restaurant feedback. Consider the emotional tone, specific comments about food, service, and overall experience.

        Respond with EXACTLY one word: 'Positive', 'Neutral', or 'Negative'.
        
        Guidelines for sentiment classification:
        
        POSITIVE - Use when feedback expresses:
        - Clear satisfaction or enjoyment ("delicious", "great", "love", "enjoyed")
        - Strong positive emotions ("happy", "pleased", "impressed")
        - Explicit praise ("service was excellent", "food was amazing")
        - Clear intent to return ("will come back", "recommend")
        
        NEGATIVE - Use when feedback expresses:
        - Any form of dissatisfaction or disappointment
        - Specific complaints ("too salty", "cold food", "slow service")
        - Negative emotions ("unhappy", "frustrated", "annoyed")
        - Price/value issues ("expensive", "not worth it")
        - Mild complaints or suggestions ("I wish...", "could be better", "should be...")
        - Service-related issues ("more patient", "faster service", "better attention")
        
        NEUTRAL - Use ONLY when:
        - Feedback is purely factual or observational
        - No clear emotional tone
        - Mixed feedback with equal positive and negative points
        - General statements without clear sentiment
        
        Examples:
        Positive: "The food was delicious and service was excellent"
        Positive: "I love the atmosphere here"
        Positive: "Best meal I've had in a long time"
        Negative: "The food was too salty"
        Negative: "Service was slow and food was cold"
        Negative: "Not worth the price"
        Negative: "I wish the server was more patient" (mild complaint)
        Negative: "Could be better" (suggestion implying dissatisfaction)
        Neutral: "The food was okay"
        Neutral: "Nice place but a bit expensive"
        
        Feedback: {text}
        
        Sentiment:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a restaurant feedback analyzer. Your task is to classify feedback as Positive, Negative, or Neutral based on the emotional tone and specific comments. Be decisive - classify mild complaints and suggestions as Negative, and only use Neutral when there is truly no clear sentiment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.7  # Increased temperature for more nuanced responses
        )
        
        sentiment = response.choices[0].message.content.strip()
        
        # Ensure we only return valid sentiment values
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            logger.warning(f"Invalid sentiment returned by API: '{sentiment}'. Using fallback analysis.")
            return fallback_sentiment_analysis(text)
        
        logger.info(f"Sentiment analysis result: '{sentiment}' for text: '{text}'")
        return sentiment
            
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return fallback_sentiment_analysis(text)

def fallback_sentiment_analysis(text):
    """Enhanced keyword-based sentiment analysis as a fallback."""
    text = text.lower()
    
    # Expanded keyword lists with weights
    positive_words = {
        'excellent': 2.0, 'amazing': 2.0, 'delicious': 2.0, 'perfect': 2.0,
        'great': 1.5, 'good': 1.5, 'love': 1.5, 'enjoyed': 1.5,
        'fresh': 1.0, 'tasty': 1.0, 'friendly': 1.0, 'quick': 1.0,
        'recommend': 1.0, 'clean': 1.0, 'authentic': 1.0, 'favorite': 1.0,
        'outstanding': 1.5, 'brilliant': 1.5, 'satisfied': 1.0, 'pleased': 1.0,
        'impressed': 1.5, 'memorable': 1.0, 'delightful': 1.5
    }
    
    negative_words = {
        'terrible': 2.0, 'awful': 2.0, 'horrible': 2.0, 'worst': 2.0,
        'disappointed': 1.5, 'bad': 1.5, 'poor': 1.5, 'not good': 1.5,
        'slow': 1.0, 'cold': 1.0, 'undercooked': 1.0, 'overcooked': 1.0,
        'salty': 1.0, 'bland': 1.0, 'rude': 1.0, 'dirty': 1.0,
        'expensive': 1.0, 'wait': 1.0, 'wrong': 1.0, 'missing': 1.0,
        'late': 1.0, 'mess': 1.0, 'dry': 1.0, 'tough': 1.0,
        'tasteless': 1.0, 'mediocre': 1.0, 'waste': 1.0, 'never again': 2.0,
        'unpleasant': 1.5, 'unacceptable': 1.5, 'complaint': 1.0,
        'issue': 1.0, 'problem': 1.0, 'disgusting': 2.0, 'inedible': 2.0,
        'wish': 1.0,  # Added for handling "I wish..." statements
        'could': 1.0,  # Added for handling "could be better" statements
        'should': 1.0,  # Added for handling "should be" statements
        'better': 1.0,  # Added for handling improvement suggestions
        'more': 1.0,   # Added for handling "more patient", "more attentive" etc.
        'less': 1.0,   # Added for handling "less salty", "less spicy" etc.
        'patient': 1.0, # Added for service-related feedback
        'attentive': 1.0,
        'faster': 1.0,
        'quicker': 1.0
    }
    
    neutral_words = {
        'okay': 0.5, 'fine': 0.5, 'average': 0.5, 'normal': 0.5,
        'regular': 0.5, 'standard': 0.5, 'typical': 0.5, 'decent': 0.5,
        'acceptable': 0.5, 'satisfactory': 0.5, 'moderate': 0.5,
        'reasonable': 0.5, 'fair': 0.5, 'alright': 0.5, 'so-so': 0.5,
        'middle': 0.5, 'neutral': 0.5, 'balanced': 0.5, 'mixed': 0.5
    }
    
    # Convert text to words for more accurate matching
    words = text.split()
    
    # Initialize scores
    pos_score = 0
    neg_score = 0
    neu_score = 0
    
    # Check for negations and their impact
    negations = ['not', 'no', 'never', "wasn't", "weren't", "isn't", "aren't", 
                 "hadn't", "doesn't", "couldn't", "wouldn't", "shouldn't"]
    
    i = 0
    while i < len(words):
        word = words[i]
        
        # Check for negations
        if word in negations and i + 1 < len(words):
            next_word = words[i + 1]
            
            # If next word is positive, count as negative
            if next_word in positive_words:
                neg_score += positive_words[next_word] * 1.2
            # If next word is negative, count as positive
            elif next_word in negative_words:
                pos_score += negative_words[next_word] * 0.8
            i += 2
            continue
            
        # Regular word scoring
        if word in positive_words:
            pos_score += positive_words[word]
        elif word in negative_words:
            neg_score += negative_words[word]
        elif word in neutral_words:
            neu_score += neutral_words[word]
            
        i += 1
    
    # Special handling for "I wish" statements
    if "wish" in text:
        neg_score += 1.0  # Boost negative score for wish statements
    
    # Special handling for "could be" and "should be" statements
    if any(phrase in text for phrase in ["could be", "should be"]):
        neg_score += 1.0  # Boost negative score for improvement suggestions
    
    # Determine sentiment based on scores
    if pos_score > neg_score and pos_score > neu_score:
        return "Positive"
    elif neg_score > pos_score and neg_score > neu_score:
        return "Negative"
    elif neu_score > pos_score and neu_score > neg_score:
        return "Neutral"
    # Default to the highest score if there's a tie
    elif pos_score >= neg_score and pos_score >= neu_score:
        return "Positive"
    elif neg_score >= pos_score and neg_score >= neu_score:
        return "Negative"
    return "Neutral" 