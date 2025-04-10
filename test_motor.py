import RPi.GPIO as GPIO
import time

# Disable warnings
GPIO.setwarnings(False)

# Setup GPIO
MOTOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

print("Testing motor on GPIO 17...")
print("Motor will turn ON for 2 seconds, then OFF for 2 seconds, 3 times")

try:
    for i in range(3):
        print(f"Test {i+1}: Turning motor ON")
        GPIO.output(MOTOR_PIN, GPIO.HIGH)
        time.sleep(2)
        print(f"Test {i+1}: Turning motor OFF")
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        time.sleep(2)
except KeyboardInterrupt:
    print("\nTest interrupted")
finally:
    GPIO.cleanup()
    print("Test complete") 