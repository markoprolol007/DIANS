from flask import Flask, render_template, jsonify, request
import pandas as pd
from datetime import datetime
import time
from pipeline import scrape_issuer_names, load_existing_data, apply_technical_indicators

app = Flask(__name__)

# Route to render the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for stock analysis
@app.route('/stock-analysis')
def stock_analysis():
    # Logic for stock analysis
    stock_names = scrape_issuer_names()
    data = load_existing_data()
    data = apply_technical_indicators(data)

    # Extract relevant stock signals (for now we're just showing a subset of the data)
    stock_signals = {}
    for name in stock_names:
        stock_data = data[data['Име'] == name].iloc[-1]
        stock_signal = generate_signal(stock_data)  # You need to define this logic
        stock_signals[name] = stock_signal

    return jsonify(stock_signals)

def generate_signal(stock_data):
    """Generate Buy/Hold/Sell signal based on indicators."""
    # Example logic: you can extend this based on your requirements
    if stock_data['RSI'] < 30:
        return 'Buy'
    elif stock_data['RSI'] > 70:
        return 'Sell'
    return 'Hold'

if __name__ == '__main__':
    app.run(debug=True)
