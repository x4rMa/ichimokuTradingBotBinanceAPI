import requests
import pandas as pd
from datetime import datetime
from ta.trend import MACD
from ta.volatility import BollingerBands
from ta.momentum import StochasticOscillator

# Function to fetch historical candle data from Binance API


def fetch_candles(symbol, interval, start_time, end_time):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                     'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)
    return df

# Function to calculate the trading strategy


def calculate_strategy(candles):
    # Convert candles to pandas DataFrame
    df = pd.DataFrame(candles, columns=[
                      'timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Calculate Bollinger Bands
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    # Calculate MACD
    macd = MACD(close=df['close'], window_slow=26,
                window_fast=12, window_sign=9)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()  # Add MACD signal line

    # Calculate Stochastic Oscillator
    stoch = StochasticOscillator(
        high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    df['%K'] = stoch.stoch()
    df['%D'] = stoch.stoch_signal()

    # Entry conditions
    df['bb_breakout_up'] = (df['close'] > df['bb_upper'].shift(1)) & (
        df['close'].shift(1) <= df['bb_upper'].shift(1))
    df['bb_breakout_down'] = (df['close'] < df['bb_lower'].shift(1)) & (
        df['close'].shift(1) >= df['bb_lower'].shift(1))
    df['macd_crossover_up'] = (df['macd'] > df['macd_signal']) & (
        df['macd'].shift(1) <= df['macd_signal'].shift(1))
    df['macd_crossover_down'] = (df['macd'] < df['macd_signal']) & (
        df['macd'].shift(1) >= df['macd_signal'].shift(1))
    df['is_oversold'] = df['%K'] < 20
    df['is_overbought'] = df['%K'] > 80

    # Exit conditions
    df['exit_conditions'] = (df['macd'] > df['macd_signal']) & (
        df['macd'].shift(1) <= df['macd_signal'].shift(1))

    # Apply the trading strategy
    df['signal'] = ''
    df.loc[df['bb_breakout_up'] & df['macd_crossover_up']
           & df['is_oversold'], 'signal'] = 'Buy'
    df.loc[df['bb_breakout_down'] & df['macd_crossover_down']
           & df['is_overbought'], 'signal'] = 'Sell'
    df.loc[df['exit_conditions'], 'signal'] = 'Exit'

    return df[['timestamp', 'close', 'bb_upper', 'bb_lower', 'macd', '%K', '%D', 'signal']]

# Backtest function


def backtest(strategy_data):
    # Initial capital
    capital = 10000
    position = 0
    trades = []

    for i in range(1, len(strategy_data)):
        current_signal = strategy_data.loc[i, 'signal']
        previous_signal = strategy_data.loc[i - 1, 'signal']
        close_price = strategy_data.loc[i, 'close']

        if current_signal == 'Buy' and previous_signal != 'Buy':
            # Enter long position
            position = capital / close_price
            trades.append(
                (strategy_data.loc[i, 'timestamp'], 'Buy', position, close_price))

        elif current_signal == 'Sell' and previous_signal != 'Sell':
            # Exit long position
            if position > 0:
                capital = position * close_price
                trades.append(
                    (strategy_data.loc[i, 'timestamp'], 'Sell', position, close_price))
                position = 0

    if position > 0:
        # Sell at the last close price if still in position
        capital = position * close_price
        trades.append((strategy_data.loc[len(
            strategy_data) - 1, 'timestamp'], 'Sell', position, close_price))
        position = 0

    return capital, trades


# Fetch historical candle data from Binance API
symbol = 'BTCUSDT'
interval = '1d'
start_time = int(datetime(2020, 1, 1).timestamp() * 1000)
end_time = int(datetime.now().timestamp() * 1000)
candles = fetch_candles(symbol, interval, start_time, end_time)

# Calculate trading strategy
strategy_data = calculate_strategy(candles)

# Perform backtest
final_capital, trades = backtest(strategy_data)

# Print results
print("Final Capital:", final_capital)
print("Trades:")
for trade in trades:
    print(trade)
