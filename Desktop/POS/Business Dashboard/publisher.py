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
    print(f"\n✨ Feedback processed at {data['timestamp']}")
    print(f"📊 Sentiment: {data['sentiment']}")

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