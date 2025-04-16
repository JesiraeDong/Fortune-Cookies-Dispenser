import socketio
import time
from datetime import datetime

# Initialize Socket.IO client with reconnection settings
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1)

# Event to track when feedback is processed
feedback_received = False

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
    global feedback_received
    try:
        feedback = data.get('feedback', {})
        sentiment = feedback.get('sentiment', 'Unknown')
        timestamp = feedback.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        suggested_tip = feedback.get('suggested_tip', '')
        cookie_message = feedback.get('cookie_message', '')
        
        stats = data.get('stats', {})
        total = stats.get('total', 0)
        positive = stats.get('positive', 0)
        neutral = stats.get('neutral', 0)
        negative = stats.get('negative', 0)
        
        print(f"\n✨ Feedback processed at {timestamp}")
        print(f"📊 Sentiment: {sentiment}")
        print(f"💰 {suggested_tip}")
        print(f"{cookie_message}")
        print(f"📈 Statistics: {total} total, {positive} positive, {neutral} neutral, {negative} negative\n")
        
        feedback_received = True
    except Exception as e:
        print(f"❌ Error processing feedback response: {str(e)}")
        feedback_received = True

def submit_feedback(feedback_text):
    """Submit feedback via WebSocket."""
    global feedback_received
    try:
        if not sio.connected:
            print("Reconnecting to server...")
            sio.connect('http://localhost:5001')
        
        # Reset the feedback received flag
        feedback_received = False
        
        # Send the feedback
        sio.emit('new_feedback', {'feedback': feedback_text})
        print(f"📤 Feedback sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Wait for feedback to be processed
        timeout = 5  # seconds
        start_time = time.time()
        while not feedback_received and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not feedback_received:
            print("⚠️ Waiting for server response...")
            
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