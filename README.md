# Business Dashboard

A real-time sentiment analysis dashboard for restaurant feedback using Flask, SocketIO, and Plotly.

## Features

- Real-time sentiment analysis of customer feedback
- Interactive visualizations:
  - Sentiment distribution pie chart
  - Sentiment trend line chart
- WebSocket-based live updates
- Responsive dashboard design

## Customer Feedback Flow Chart

```mermaid
flowchart LR
    %% Define subgraphs with styling
    subgraph CustomerSide["Customer Side"]
        style CustomerSide fill:#e6f7ff,stroke:#1890ff,stroke-width:2px
        CT["Customer Terminal"]
        EF["Enter Feedback"]
        SF["Send Feedback"]
    end

    subgraph Backend["Backend"]
        style Backend fill:#f6ffed,stroke:#52c41a,stroke-width:2px
        FSS["Flask SocketIO Server"]
        RF["Receive Feedback"]
        SA["Sentiment Analysis"]
        STF["Store Feedback"]
        ER["Emit Result"]
        TS["Trigger Servo"]
    end

    subgraph BusinessSide["Business Side"]
        style BusinessSide fill:#fff1f0,stroke:#f5222d,stroke-width:2px
        BD["Business Dashboard"]
        DV["Display Visualizations"]
        AD["Access Dashboard"]
    end

    %% Define connections with labels
    CT --> EF
    EF --> SF
    SF -->|"Feedback via WebSocket"| FSS
    FSS --> RF
    RF -->|"Sentiment Analysis via OpenAI"| SA
    SA -->|"Store in SQLite"| STF
    STF --> ER
    ER -->|"Trigger Servo (optional)"| TS
    ER -->|"Update Dashboard"| BD
    BD --> DV
    DV -->|"Access via /dashboard route"| AD
    CT <--|"Emit Result"| ER

    %% Apply styling to nodes
    classDef terminal fill:#e6f7ff,stroke:#1890ff,stroke-width:2px
    classDef server fill:#f6ffed,stroke:#52c41a,stroke-width:2px
    classDef dashboard fill:#fff1f0,stroke:#f5222d,stroke-width:2px
    classDef process fill:#f9f0ff,stroke:#722ed1,stroke-width:1px

    %% Apply classes to nodes
    class CT,EF,SF terminal
    class FSS server
    class RF,SA,STF,ER,TS process
    class BD,DV,AD dashboard
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the subscriber server:
```bash
python sub.py
```

3. Run the publisher to submit feedback:
```bash
python publisher.py
```

4. Access the dashboard at http://localhost:5001

## Project Structure

- `sub.py`: Flask server with WebSocket support and dashboard
- `publisher.py`: Feedback submission interface
- `sentiment.py`: Sentiment analysis module
- `models.py`: Database models
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files

## Technologies Used

- Flask
- Flask-SocketIO
- Plotly
- SQLAlchemy
- OpenAI GPT-3.5 