import socketio
import time
import json
import logging
import RPi.GPIO as GPIO
from datetime import datetime

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

class MotorController:
    def __init__(self):
        # Initialize Socket.IO client with reconnection settings
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1)
        
        # Set up event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('connect_error', self.on_connect_error)
        self.sio.on('feedback_processed', self.on_feedback_processed)
        
        # Initialize stepper motor
        self.motor = StepperMotor()
        
    def on_connect(self):
        """Handle connection event"""
        logger.info("✅ Connected to server!")
        
    def on_disconnect(self):
        """Handle disconnection event"""
        logger.info("❌ Disconnected from server - attempting to reconnect...")
        
    def on_connect_error(self, data):
        """Handle connection error event"""
        logger.error(f"❌ Connection error: {data}")
        
    def on_feedback_processed(self, data):
        """Handle feedback processed event"""
        try:
            # Extract feedback data
            feedback = data.get('feedback', {})
            sentiment = feedback.get('sentiment', 'Unknown')
            
            # Check if sentiment is positive
            if sentiment.lower() == 'positive':
                logger.info("Positive sentiment detected! Dispensing fortune cookie...")
                # Rotate motor 360 degrees clockwise to dispense cookie
                self.motor.rotate(360, 1)
                logger.info("Fortune cookie dispensed!")
            else:
                logger.info(f"Received {sentiment} sentiment - no action needed")
                
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
    
    def start(self):
        """Start the motor controller"""
        try:
            # Connect to the Flask-SocketIO server
            logger.info("Connecting to server...")
            self.sio.connect('http://localhost:5001')
            
            # Keep the connection alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping motor controller...")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            if self.sio.connected:
                self.sio.disconnect()
            self.motor.cleanup()

def main():
    print("\n🔄 Fortune Cookie Motor Controller")
    print("--------------------------------")
    print("Press Ctrl+C to exit\n")
    
    controller = MotorController()
    controller.start()

if __name__ == "__main__":
    main() 