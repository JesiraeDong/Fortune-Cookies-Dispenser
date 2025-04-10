import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO
import time

# Disable GPIO warnings
GPIO.setwarnings(False)

# GPIO Configuration
MOTOR_PIN = 17
LED_PIN = 18
BUTTON_PIN = 27

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "sentiment/feedback"

print("Setting up GPIO...")
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize pins to LOW
GPIO.output(MOTOR_PIN, GPIO.LOW)
GPIO.output(LED_PIN, GPIO.LOW)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(mqtt_topic)
    print(f"Subscribed to topic: {mqtt_topic}")

def on_message(client, userdata, msg):
    try:
        print(f"Received message: {msg.payload.decode()}")
        data = json.loads(msg.payload.decode())
        sentiment = data.get('sentiment', '').lower()
        print(f"Processing sentiment: {sentiment}")
        
        if sentiment == 'positive':
            print("Dispensing fortune cookie...")
            print("Turning motor ON")
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            time.sleep(2)
            print("Turning motor OFF")
            GPIO.output(MOTOR_PIN, GPIO.LOW)
        elif sentiment == 'neutral':
            print("Blinking LED...")
            for _ in range(3):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.5)
    except Exception as e:
        print(f"Error processing message: {e}")

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Starting microcontroller...")
try:
    # Connect to MQTT broker
    print("Connecting to MQTT broker...")
    client.connect(mqtt_broker, mqtt_port, 60)
    print("Starting MQTT loop...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    print("Cleaning up...")
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup() 