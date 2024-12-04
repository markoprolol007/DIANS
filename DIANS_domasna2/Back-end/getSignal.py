import pandas as pd

data = pd.read_csv('appliedIndicators.csv')

def stock_signal(stock_name, data):
    stock_data = data[data['Име'] == stock_name].iloc[-1]

    if stock_data['RSI'] > 70:
        rsi_signal = "Sell"
    elif stock_data['RSI'] < 30:
        rsi_signal = "Buy"
    else:
        rsi_signal = "Hold"

    if stock_data['MACD'] > stock_data['MACD_Signal']:
        macd_signal = "Buy"
    elif stock_data['MACD'] < stock_data['MACD_Signal']:
        macd_signal = "Sell"
    else:
        macd_signal = "Hold"

    if stock_data['Stochastic'] > 80:
        stochastic_signal = "Sell"
    elif stock_data['Stochastic'] < 20:
        stochastic_signal = "Buy"
    else:
        stochastic_signal = "Hold"

    if stock_data['Цена на последна трансакција'] > stock_data['BB_Upper']:
        bb_signal = "Sell"
    elif stock_data['Цена на последна трансакција'] < stock_data['BB_Lower']:
        bb_signal = "Buy"
    else:
        bb_signal = "Hold"

    if stock_data['CCI'] > 100:
        cci_signal = "Buy"
    elif stock_data['CCI'] < -100:
        cci_signal = "Sell"
    else:
        cci_signal = "Hold"

    signals = [rsi_signal, macd_signal, stochastic_signal, bb_signal, cci_signal]
    buy_signals = signals.count("Buy")
    sell_signals = signals.count("Sell")

    if buy_signals >= 3:
        final_signal = "Buy"
    elif sell_signals >= 3:
        final_signal = "Sell"
    else:
        final_signal = "Hold"

    return final_signal

if __name__ == '__main__':
    print(
    stock_signal('', data)
    )

