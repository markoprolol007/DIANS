from flask import Flask, jsonify, request
import pandas as pd
import os
from datetime import date

# Initialize Flask app
app = Flask(__name__)

# Path to the CSV file
CSV_FILE_PATH = "../appliedIndicators.csv"


# Helper function to load stock data
def load_stock_data():
    if not os.path.exists(CSV_FILE_PATH):
        raise FileNotFoundError(f"CSV file not found at {CSV_FILE_PATH}")
    df = pd.read_csv(CSV_FILE_PATH)
    df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce')
    df = df.dropna(subset=['Датум'])
    return df


# Route to get stock data with indicators
@app.route('/get_stocks_with_indicators', methods=['GET'])
def get_stocks_with_indicators():
    try:
        # Load stock data
        df = load_stock_data()

        # Get the closest date to today
        today = pd.to_datetime(date.today())
        closest_date = df[df['Датум'] <= today]['Датум'].max()

        if pd.isna(closest_date):
            return jsonify({"error": "No stock data available"}), 404

        # Filter data for the closest date
        filtered_data = df[df['Датум'] == closest_date]

        # Build the response
        stocks_with_indicators = []
        for _, row in filtered_data.iterrows():
            stock_info = {
                "name": row['Име'],
                "price": float(row['Цена на последна трансакција']),
                "indicators": {
                    "RSI": row.get('RSI'),
                    "CCI": row.get('CCI'),
                    "Stochastic": row.get('Stochastic'),
                    "MACD": row.get('MACD'),
                    "SMA_20": row.get('SMA_20'),
                    "SMA_50": row.get('SMA_50'),
                    "EMA_20": row.get('EMA_20'),
                    "EMA_50": row.get('EMA_50'),
                    "Bollinger_Upper": row.get('Bollinger_Upper'),
                    "Bollinger_Lower": row.get('Bollinger_Lower'),
                }
            }
            stocks_with_indicators.append(stock_info)

        return jsonify({
            "date": closest_date.strftime('%d.%m.%Y'),
            "stocks": stocks_with_indicators
        })

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Main entry point for running the service
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
