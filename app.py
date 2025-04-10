from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_socketio import SocketIO
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "feedback/updates"

# Database setup
def init_db():
    if not os.path.exists('feedback.db'):
        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE feedback
                    (text TEXT, sentiment TEXT, timestamp TEXT)''')
        conn.commit()
        conn.close()

def get_feedback_data():
    conn = sqlite3.connect('feedback.db')
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    return df

def create_charts():
    df = get_feedback_data()
    
    if df.empty:
        # Return empty charts if no data
        pie_chart = {
            'data': [{'values': [], 'labels': [], 'type': 'pie'}],
            'layout': {'title': 'Sentiment Distribution'}
        }
        line_chart = {
            'data': [{'x': [], 'y': [], 'type': 'scatter'}],
            'layout': {'title': 'Sentiment Trend'}
        }
        return pie_chart, line_chart
    
    # Create pie chart
    sentiment_counts = df['sentiment'].value_counts()
    pie_chart = {
        'data': [{
            'values': sentiment_counts.values,
            'labels': sentiment_counts.index,
            'type': 'pie',
            'marker': {
                'colors': ['#2ecc71', '#f1c40f', '#e74c3c']
            }
        }],
        'layout': {
            'title': 'Sentiment Distribution',
            'showlegend': True
        }
    }
    
    # Create line chart
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.floor('H')
    hourly_sentiment = df.groupby('hour')['sentiment'].apply(
        lambda x: pd.Series({
            'positive': (x == 'positive').mean(),
            'neutral': (x == 'neutral').mean(),
            'negative': (x == 'negative').mean()
        })
    ).reset_index()
    
    line_chart = {
        'data': [
            {
                'x': hourly_sentiment['hour'],
                'y': hourly_sentiment['positive'],
                'name': 'Positive',
                'type': 'scatter',
                'mode': 'lines+markers',
                'line': {'color': '#2ecc71'}
            },
            {
                'x': hourly_sentiment['hour'],
                'y': hourly_sentiment['neutral'],
                'name': 'Neutral',
                'type': 'scatter',
                'mode': 'lines+markers',
                'line': {'color': '#f1c40f'}
            },
            {
                'x': hourly_sentiment['hour'],
                'y': hourly_sentiment['negative'],
                'name': 'Negative',
                'type': 'scatter',
                'mode': 'lines+markers',
                'line': {'color': '#e74c3c'}
            }
        ],
        'layout': {
            'title': 'Sentiment Trend',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Proportion'},
            'showlegend': True
        }
    }
    
    return pie_chart, line_chart

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        if data['type'] == 'new_feedback':
            # Store feedback in database
            conn = sqlite3.connect('feedback.db')
            c = conn.cursor()
            c.execute("INSERT INTO feedback VALUES (?, ?, ?)",
                     (data['feedback']['text'],
                      data['feedback']['sentiment'],
                      data['feedback']['timestamp']))
            conn.commit()
            conn.close()
            
            # Update charts
            pie_chart, line_chart = create_charts()
            
            # Emit updates through WebSocket
            socketio.emit('feedback_processed', {
                'type': 'charts_update',
                'pie_chart': json.dumps(pie_chart),
                'line_chart': json.dumps(line_chart)
            })
            
    except Exception as e:
        print(f"Error processing message: {e}")
        socketio.emit('feedback_error', {
            'type': 'error',
            'message': str(e)
        })

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    pie_chart, line_chart = create_charts()
    return render_template('dashboard.html',
                         pie_chart=json.dumps(pie_chart),
                         line_chart=json.dumps(line_chart))

if __name__ == '__main__':
    init_db()
    try:
        mqtt_client.connect(mqtt_broker, mqtt_port, 60)
        mqtt_client.loop_start()
        socketio.run(app, debug=True, port=5001)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect() 