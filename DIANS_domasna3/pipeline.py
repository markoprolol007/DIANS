import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator, CCIIndicator
from ta.volatility import BollingerBands

def scrape_issuer_names():
    response = requests.get('https://www.mse.mk/mk/stats/symbolhistory/kmb')
    soup = BeautifulSoup(response.text, 'html.parser')
    return [option.text for option in soup.find_all('option') if not any(char.isdigit() for char in option.text)]

def get_data_for(code, start_date, end_date):
    url = f'https://www.mse.mk/mk/stats/symbolhistory/{code}'
    data = {'FromDate': start_date.strftime('%d.%m.%Y'), 'ToDate': end_date.strftime('%d.%m.%Y'), 'Code': code}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headers = [th.text.strip() for th in soup.find_all('th')]
        rows = [[code] + [td.text.strip() for td in row.find_all('td')] for row in soup.find_all('tr')[1:]]
        return pd.DataFrame(rows, columns=['Име'] + headers)
    return pd.DataFrame()

def load_existing_data(filename='data.csv'):
    try:
        return pd.read_csv(filename, parse_dates=['Датум'], dayfirst=True)
    except FileNotFoundError:
        return pd.DataFrame()

def update_data_for_issuers(names, existing_data, filename='data.csv'):
    today = datetime.now()
    new_data = pd.DataFrame()
    for name in names:
        start_date = today - timedelta(days=365 * 10) if name not in existing_data['Име'].values else existing_data[existing_data['Име'] == name]['Датум'].max() + timedelta(days=1)
        if start_date < today:
            new_data = pd.concat([new_data, get_data_for(name, start_date, today)], ignore_index=True)
    save_filtered_data(new_data, filename)

def save_filtered_data(new_data, filename='data.csv'):
    new_data = new_data[new_data['Количина'] != '0']
    append_mode = 'a' if pd.io.common.file_exists(filename) else 'w'
    new_data.to_csv(filename, mode=append_mode, index=False, header=append_mode == 'w')

def filter_data(data):
    data['Количина'] = pd.to_numeric(data['Количина'], errors='coerce')
    return data[data['Количина'] != 0]

def sort_data(data):
    data['Датум'] = pd.to_datetime(data['Датум'], errors='coerce')
    return data.sort_values(['Име', 'Датум']).reset_index(drop=True)

def apply_technical_indicators(data):
    numeric_columns = ['Цена на последна трансакција', 'Мак.', 'Мин.']
    for col in numeric_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col].str.replace(',', '.').str.replace(r'\.(?=\d*\.)', '', regex=True).str.replace(' ', ''), errors='coerce')
    indicators = {
        'RSI': lambda df: RSIIndicator(close=df['Цена на последна трансакција']).rsi(),
        'Stochastic': lambda df: StochasticOscillator(high=df['Мак.'], low=df['Мин.'], close=df['Цена на последна трансакција']).stoch(),
        'MACD': lambda df: MACD(close=df['Цена на последна трансакција']).macd(),
        'SMA_20': lambda df: SMAIndicator(close=df['Цена на последна трансакција'], window=20).sma_indicator(),
        'EMA_20': lambda df: EMAIndicator(close=df['Цена на последна трансакција'], window=20).ema_indicator(),
        'SMA_50': lambda df: SMAIndicator(close=df['Цена на последна трансакција'], window=50).sma_indicator(),
        'EMA_50': lambda df: EMAIndicator(close=df['Цена на последна трансакција'], window=50).ema_indicator(),
        'CCI': lambda df: CCIIndicator(high=df['Мак.'], low=df['Мин.'], close=df['Цена на последна трансакција']).cci(),
        'Bollinger_Upper': lambda df: BollingerBands(close=df['Цена на последна трансакција'], window=20, window_dev=2).bollinger_hband(),
        'Bollinger_Lower': lambda df: BollingerBands(close=df['Цена на последна трансакција'], window=20, window_dev=2).bollinger_lband(),
    }
    for name, func in indicators.items():
        data[name] = func(data)
    return data.round(2)

def main():
    start_time = time.time()
    names = scrape_issuer_names()
    existing_data = load_existing_data()
    update_data_for_issuers(names, existing_data)
    data = load_existing_data()
    data = filter_data(data)
    data = sort_data(data)
    data = apply_technical_indicators(data)
    data.to_csv('appliedIndicators.csv', index=False)
    print(f"Pipeline completed in {time.time() - start_time:.2f} seconds. Data saved to 'appliedIndicators.csv'.")

if __name__ == "__main__":
    main()
