import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GPIO pins for stepper motor
STEPPER_PINS = {
    'IN1': 17,  # GPIO17
    'IN2': 18,  # GPIO18
    'IN3': 27,  # GPIO27
    'IN4': 22   # GPIO22
}

# Stepper motor sequence (8-step sequence for smoother motion)
STEP_SEQUENCE = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

class StepperMotor:
    def __init__(self):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in STEPPER_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
        
        self.current_step = 0
        self.steps_per_revolution = 2048  # For 28BYJ-48 motor
        self.delay = 0.001  # 1ms delay between steps
        
    def step(self, steps=1, direction=1):
        """
        Move the stepper motor a specified number of steps
        :param steps: Number of steps to move
        :param direction: 1 for clockwise, -1 for counter-clockwise
        """
        for _ in range(steps):
            # Get current step pattern
            pattern = STEP_SEQUENCE[self.current_step]
            
            # Set GPIO pins according to pattern
            for i, pin in enumerate(STEPPER_PINS.values()):
                GPIO.output(pin, pattern[i])
            
            # Move to next step
            self.current_step = (self.current_step + direction) % len(STEP_SEQUENCE)
            time.sleep(self.delay)
    
    def rotate(self, degrees=360, direction=1):
        """
        Rotate the motor by a specified number of degrees
        :param degrees: Degrees to rotate
        :param direction: 1 for clockwise, -1 for counter-clockwise
        """
        steps = int((degrees / 360) * self.steps_per_revolution)
        self.step(steps, direction)
    
    def cleanup(self):
        """Clean up GPIO pins"""
        for pin in STEPPER_PINS.values():
            GPIO.output(pin, 0)
        GPIO.cleanup()

class MQTTMotorController:
    def __init__(self, broker="localhost", port=1883, topic="sentiment/feedback"):
        self.motor = StepperMotor()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.broker = broker
        self.port = port
        self.topic = topic
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        logger.info(f"Connected to MQTT broker with result code {rc}")
        client.subscribe(self.topic)
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            payload = json.loads(msg.payload.decode())
            sentiment = payload.get('sentiment', '').lower()
            
            if sentiment == 'positive':
                logger.info("Positive sentiment detected! Dispensing fortune cookie...")
                # Rotate motor 360 degrees clockwise to dispense cookie
                self.motor.rotate(360, 1)
                logger.info("Fortune cookie dispensed!")
            else:
                logger.info(f"Received {sentiment} sentiment - no action needed")
                
        except json.JSONDecodeError:
            logger.error("Failed to decode message payload")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def start(self):
        """Start the MQTT client"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Stopping motor controller...")
        finally:
            self.motor.cleanup()

if __name__ == "__main__":
    # Create and start the motor controller
    controller = MQTTMotorController()
    controller.start() 