# Fortune Cookie Motor Controller

This is a standalone motor controller that integrates with the existing sentiment analysis system to dispense fortune cookies when positive sentiment is detected.

## Overview

The motor controller listens to the same WebSocket events as the publisher but focuses on controlling the stepper motor when positive sentiment is detected. This allows you to add motor control functionality without modifying your existing code.

## Hardware Requirements

- Raspberry Pi (for motor control)
- 28BYJ-48 Stepper Motor
- ULN2003 Motor Driver
- Jumper wires
- Power supply (5V)

## GPIO Pin Configuration

The stepper motor uses the following GPIO pins on the Raspberry Pi:
- IN1: GPIO17
- IN2: GPIO18
- IN3: GPIO27
- IN4: GPIO22

## How It Works

1. The motor controller connects to the same WebSocket server as the publisher
2. It listens for the 'feedback_processed' event
3. When a positive sentiment is detected, it activates the stepper motor
4. The motor rotates 360 degrees to dispense a fortune cookie

## Usage

1. Make sure your Flask server (sub.py) is running
2. Run the motor controller:
```bash
python motor_controller.py
```
3. Run the publisher as usual:
```bash
python publisher.py
```
4. Submit feedback through the publisher
5. When positive sentiment is detected, the motor will activate

## Integration with Existing System

The motor controller works alongside your existing system:

- **Publisher (publisher.py)**: Submits feedback and receives sentiment analysis
- **Flask Server (sub.py)**: Processes feedback and broadcasts results
- **Motor Controller (motor_controller.py)**: Listens for positive sentiment and controls the motor

This modular approach allows you to add motor control without modifying your existing code.

## Troubleshooting

- **Motor not moving**: Check GPIO connections and power supply
- **Connection issues**: Ensure the Flask server is running on port 5001
- **GPIO errors**: Make sure you're running with sufficient permissions (sudo)

## Notes

- The motor controller uses the same WebSocket events as the publisher
- It only activates the motor for positive sentiment
- The stepper motor uses an 8-step sequence for smooth operation
- The motor rotates 360 degrees to dispense a fortune cookie 