import socketio
import time
from datetime import datetime

# Initialize Socket.IO client with reconnection settings
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1)

@sio.event
def connect():
    print("✅ Connected to server!")

@sio.event
def disconnect():
    print("❌ Disconnected from server - attempting to reconnect...")

@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")

@sio.event
def connection_response(data):
    print(f"🔄 Server response: {data['data']}")

@sio.event
def feedback_processed(data):
    """Handle processed feedback response from server"""
    try:
        # Extract feedback data
        feedback = data.get('feedback', {})
        sentiment = feedback.get('sentiment', 'Unknown')
        timestamp = feedback.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Extract statistics
        stats = data.get('stats', {})
        total = stats.get('total', 0)
        positive = stats.get('positive', 0)
        neutral = stats.get('neutral', 0)
        negative = stats.get('negative', 0)
        
        # Define suggested tips based on sentiment
        suggested_tips = {
            "Positive": "💖 Suggested Tip: 25%, 20%, or Custom",
            "Neutral": "🌿 Suggested Tip: 20%, 18%, or Custom",
            "Negative": "💙 Suggested Tip: 15% or Custom"
        }
        
        # Print feedback information
        print(f"\n✨ Feedback processed at {timestamp}")
        print(f"📊 Sentiment: {sentiment}")
        print(f"💰 {suggested_tips.get(sentiment, '💫 Suggested Tip: Custom')}")
        print(f"🍪 Fortune cookie has been dispensed!")
        print(f"📈 Statistics: {total} total, {positive} positive, {neutral} neutral, {negative} negative")
        
    except Exception as e:
        print(f"❌ Error processing feedback response: {str(e)}")
        print(f"Raw data received: {data}")

def submit_feedback(feedback_text):
    """Submit feedback via WebSocket."""
    try:
        if not sio.connected:
            print("Reconnecting to server...")
            sio.connect('http://localhost:5001')
            
        sio.emit('new_feedback', {'feedback': feedback_text})
        print(f"📤 Feedback sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    except Exception as e:
        print(f"❌ Error sending feedback: {str(e)}")
        return False

def main():
    print("🔄 Restaurant Feedback Publisher")
    print("--------------------------------")
    print("Type 'quit' to exit\n")
    
    try:
        # Connect to the Flask-SocketIO server
        sio.connect('http://localhost:5001')
        
        while True:
            try:
                feedback = input("\n📝 Enter customer feedback: ").strip()
                
                if feedback.lower() == 'quit':
                    print("\n👋 Goodbye!")
                    break
                    
                if feedback:
                    submit_feedback(feedback)
                else:
                    print("❌ Error: Feedback cannot be empty")
                
                time.sleep(1)  # Small delay between submissions
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                time.sleep(2)  # Wait before retrying
                
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == '__main__':
    main() 