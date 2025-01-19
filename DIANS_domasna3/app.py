from datetime import date
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)


CSV_FILE_PATH = "appliedIndicators.csv"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stockAnalysis')
def stock_analysis():
    return render_template('stockAnalysis.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/get_stock_data', methods=['GET'])
def get_stock_data():
    if not os.path.exists(CSV_FILE_PATH):
        return jsonify({"error": f"CSV file not found at {CSV_FILE_PATH}"}), 404

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce')
        df = df.dropna(subset=['Датум'])
        df = df.sort_values('Датум', ascending=False)
        today = pd.to_datetime(date.today())
        closest_date = df[df['Датум'] <= today]['Датум'].max()

        if pd.isna(closest_date):
            return jsonify({"error": "No stock data available"}), 404

        stocks = df[df['Датум'] == closest_date][['Име', 'Цена на последна трансакција']]

        stock_mapping = {
            "ALK": "Алкалоид АД Скопје",
            "KMB": "Комерцијална банка АД Скопје",
            "MPT": "Макпетрол АД Скопје"
        }

        filtered_stocks = []
        for _, row in stocks.iterrows():
            stock_code = row['Име']
            if stock_code in stock_mapping:
                filtered_stocks.append({
                    'name': stock_mapping[stock_code],
                    'price': float(row['Цена на последна трансакција'])
                })

        return jsonify({
            "date": closest_date.strftime('%d.%m.%Y'),
            "stocks": filtered_stocks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_dropdown_values', methods=['GET'])
def get_dropdown_values():

    if not os.path.exists(CSV_FILE_PATH):
        return jsonify({"error": f"CSV file not found at {CSV_FILE_PATH}"}), 404

    try:

        df = pd.read_csv(CSV_FILE_PATH)
        unique_values = df["Име"].dropna().unique().tolist()
        return jsonify(unique_values)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_indicator_values', methods=['GET'])
def get_indicator_values():
    stock_name = request.args.get('stock_name')
    if not stock_name:
        return jsonify({"error": "Missing 'stock_name' query parameter"}), 400

    if not os.path.exists(CSV_FILE_PATH):
        return jsonify({"error": f"CSV file not found at {CSV_FILE_PATH}"}), 404

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce')
        df = df.dropna(subset=['Датум'])
        df = df.sort_values('Датум', ascending=False)
        today = pd.to_datetime(date.today())
        closest_date = df[df['Датум'] <= today]['Датум'].max()

        if pd.isna(closest_date):
            return jsonify({"error": "No indicator data available"}), 404

        filtered_data = df[(df['Датум'] == closest_date) & (df['Име'] == stock_name)]

        if filtered_data.empty:
            return jsonify({"error": f"No data available for stock '{stock_name}'"}), 404

        indicators = filtered_data[['RSI', 'CCI', 'Stochastic', 'MACD', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'Bollinger_Upper', 'Bollinger_Lower']].iloc[0].to_dict()
        price = filtered_data['Цена на последна трансакција'].iloc[0]

        return jsonify({
            "date": closest_date.strftime('%d.%m.%Y'),
            "stock_name": stock_name,
            "price": price,
            "indicators": indicators
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
