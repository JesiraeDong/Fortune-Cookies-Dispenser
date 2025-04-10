import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "sentiment/feedback"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
    else:
        print(f"Failed to connect to MQTT broker with code: {rc}")

def submit_feedback(client, text, sentiment):
    feedback_data = {
        'text': text,
        'sentiment': sentiment,
        'timestamp': datetime.now().isoformat()
    }
    client.publish(mqtt_topic, json.dumps(feedback_data))
    print(f"Published feedback: {text} ({sentiment})")

def main():
    # Create MQTT client with the latest API version
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    
    try:
        # Connect to MQTT broker
        print("Connecting to MQTT broker...")
        client.connect(mqtt_broker, mqtt_port, 60)
        client.loop_start()
        
        while True:
            print("\nEnter feedback (or 'quit' to exit):")
            text = input("Feedback text: ")
            if text.lower() == 'quit':
                break
                
            print("\nSelect sentiment:")
            print("1. Positive")
            print("2. Neutral")
            print("3. Negative")
            
            choice = input("Enter choice (1-3):")
            sentiment_map = {
                '1': 'positive',
                '2': 'neutral',
                '3': 'negative'
            }
            
            if choice in sentiment_map:
                sentiment = sentiment_map[choice]
                submit_feedback(client, text, sentiment)
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main() 