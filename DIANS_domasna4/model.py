import pandas as pd
import os
from datetime import date

CSV_FILE_PATH = "appliedIndicators.csv"


class StockModel:
    @staticmethod
    def load_stock_data():
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"CSV file not found at {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
        df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce')
        df = df.dropna(subset=['Датум'])
        return df

    @staticmethod
    def get_latest_stock_data():
        df = StockModel.load_stock_data()
        today = pd.to_datetime(date.today())
        closest_date = df[df['Датум'] <= today]['Датум'].max()

        if pd.isna(closest_date):
            raise ValueError("No stock data available")

        stocks = df[df['Датум'] == closest_date][['Име', 'Цена на последна трансакција']]
        return closest_date, stocks

    @staticmethod
    def get_dropdown_values():
        df = StockModel.load_stock_data()
        return df["Име"].dropna().unique().tolist()

    @staticmethod
    def get_indicator_values(stock_name):
        df = StockModel.load_stock_data()
        today = pd.to_datetime(date.today())
        closest_date = df[df['Датум'] <= today]['Датум'].max()

        if pd.isna(closest_date):
            raise ValueError("No indicator data available")

        filtered_data = df[(df['Датум'] == closest_date) & (df['Име'] == stock_name)]

        if filtered_data.empty:
            raise ValueError(f"No data available for stock '{stock_name}'")

        indicators = filtered_data[['RSI', 'CCI', 'Stochastic', 'MACD', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50',
                                    'Bollinger_Upper', 'Bollinger_Lower']].iloc[0].to_dict()
        price = filtered_data['Цена на последна трансакција'].iloc[0]

        return closest_date, stock_name, price, indicators
