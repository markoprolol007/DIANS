import pandas as pd

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator, CCIIndicator
from ta.volatility import BollingerBands

data = pd.read_csv('filtered.csv')


def calculate_rsi(data, column='Цена на последна трансакција', window=14):
    if column in data.columns:
        data['RSI'] = RSIIndicator(close=data[column], window=window).rsi()
    else:
        print(f"Warning: Column '{column}' is missing. RSI not calculated.")
    return data


def calculate_stochastic_oscillator(data, high_col='Мак.', low_col='Мин.', close_col='Цена на последна трансакција',
                                    window=14):
    if all(col in data.columns for col in [high_col, low_col, close_col]):
        stoch = StochasticOscillator(
            high=data[high_col], low=data[low_col], close=data[close_col], window=window
        )
        data['Stochastic'] = stoch.stoch()
        data['Stochastic_Signal'] = stoch.stoch_signal()
    else:
        print(
            f"Warning: Required columns '{high_col}', '{low_col}', or '{close_col}' are missing. Stochastic Oscillator not calculated.")
    return data


def calculate_macd(data, column='Цена на последна трансакција', window_slow=26, window_fast=12, window_sign=9):
    if column in data.columns:
        macd = MACD(close=data[column], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        data['MACD_Diff'] = macd.macd_diff()
    else:
        print(f"Warning: Column '{column}' is missing. MACD not calculated.")
    return data


def calculate_sma(data, column='Цена на последна трансакција', window=20):
    if column in data.columns:
        data[f'SMA_{window}'] = SMAIndicator(close=data[column], window=window).sma_indicator()
    else:
        print(f"Warning: Column '{column}' is missing. SMA not calculated.")
    return data


def calculate_ema(data, column='Цена на последна трансакција', window=20):
    if column in data.columns:
        data[f'EMA_{window}'] = EMAIndicator(close=data[column], window=window).ema_indicator()
    else:
        print(f"Warning: Column '{column}' is missing. EMA not calculated.")
    return data


def calculate_bollinger_bands(data, column='Цена на последна трансакција', window=20, window_dev=2):
    if column in data.columns:
        bb = BollingerBands(close=data[column], window=window, window_dev=window_dev)
        data['BB_Upper'] = bb.bollinger_hband()
        data['BB_Lower'] = bb.bollinger_lband()
        data['BB_Mean'] = bb.bollinger_mavg()
    else:
        print(f"Warning: Column '{column}' is missing. Bollinger Bands not calculated.")
    return data


def calculate_cci(data, high_col='Мак.', low_col='Мин.', close_col='Цена на последна трансакција', window=20):
    if all(col in data.columns for col in [high_col, low_col, close_col]):
        data['CCI'] = CCIIndicator(high=data[high_col], low=data[low_col], close=data[close_col], window=window).cci()
    else:
        print(f"Warning: Required columns '{high_col}', '{low_col}', or '{close_col}' are missing. CCI not calculated.")
    return data


def apply_technical_indicators(data):
    numeric_columns = ['Цена на последна трансакција', 'Мак.', 'Мин.']
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].astype(str)
            data[col] = data[col].str.replace(',', '.')
            data[col] = data[col].str.replace(r'\.(?=\d*\.)', '', regex=True)
            data[col] = data[col].str.replace(' ', '')
            data[col] = pd.to_numeric(data[col], errors='coerce')

    data = calculate_rsi(data)
    data = calculate_stochastic_oscillator(data)
    data = calculate_macd(data)
    data = calculate_sma(data, window=20)
    data = calculate_ema(data, window=20)
    data = calculate_bollinger_bands(data)
    data = calculate_cci(data)

    data = data.round(2)

    return data


data = apply_technical_indicators(data)

data.to_csv('appliedIndicators.csv', index=False)
print("Updated data with indicators has been saved to 'filtered.csv'.")
