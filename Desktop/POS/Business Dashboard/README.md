# Fortune Cookie Dispenser

A Raspberry Pi-based fortune cookie dispenser that responds to customer feedback sentiment.

## Hardware Requirements

- Raspberry Pi
- Motor (connected to GPIO 17)
- LED (connected to GPIO 18)
- Button (connected to GPIO 27)
- MQTT Broker (Mosquitto)

## Software Requirements

- Python 3.x
- paho-mqtt
- RPi.GPIO
- Mosquitto MQTT Broker

## Installation

1. Install required system packages:
```bash
sudo apt update
sudo apt install python3-venv python3-full mosquitto mosquitto-clients
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python packages:
```bash
pip install paho-mqtt RPi.GPIO
```

## Usage

1. Start the MQTT broker:
```bash
sudo systemctl start mosquitto
```

2. Run the microcontroller script:
```bash
sudo venv/bin/python microcontroller.py
```

3. In a separate terminal, run the publisher:
```bash
cd ~/fortune_cookie
source venv/bin/activate
python publisher.py
```

4. Enter feedback and select sentiment:
   - 1: Positive (triggers motor)
   - 2: Neutral (triggers LED)
   - 3: Negative (no action)

## Testing

To test the motor connection:
```bash
sudo venv/bin/python test_motor.py
```

## Troubleshooting

1. Check MQTT broker status:
```bash
sudo systemctl status mosquitto
```

2. Verify GPIO connections:
- Motor: GPIO 17
- LED: GPIO 18
- Button: GPIO 27

3. Check permissions:
```bash
sudo usermod -a -G gpio $USER
```

## License

MIT License 