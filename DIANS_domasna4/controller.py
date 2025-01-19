from flask import Flask, render_template, jsonify, request
from model import StockModel

app = Flask(__name__)

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
    try:
        closest_date, stocks = StockModel.get_latest_stock_data()
        stock_mapping = {
            "ALK": "Алкалоид АД Скопје",
            "KMB": "Комерцијална банка АД Скопје",
            "MPT": "Макпетрол АД Скопје"
        }

        filtered_stocks = [
            {
                'name': stock_mapping.get(row['Име'], row['Име']),
                'price': float(row['Цена на последна трансакција'])
            }
            for _, row in stocks.iterrows() if row['Име'] in stock_mapping
        ]

        return jsonify({
            "date": closest_date.strftime('%d.%m.%Y'),
            "stocks": filtered_stocks
        })

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_dropdown_values', methods=['GET'])
def get_dropdown_values():
    try:
        values = StockModel.get_dropdown_values()
        return jsonify(values)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_indicator_values', methods=['GET'])
def get_indicator_values():
    stock_name = request.args.get('stock_name')
    if not stock_name:
        return jsonify({"error": "Missing 'stock_name' query parameter"}), 400

    try:
        closest_date, stock_name, price, indicators = StockModel.get_indicator_values(stock_name)
        return jsonify({
            "date": closest_date.strftime('%d.%m.%Y'),
            "stock_name": stock_name,
            "price": price,
            "indicators": indicators
        })

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
