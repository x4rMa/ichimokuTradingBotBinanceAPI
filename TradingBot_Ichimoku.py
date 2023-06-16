from datetime import datetime
import ccxt
import datetime
from binance.client import Client
import pandas as pd
import time
import math
import getpass
import sys


def check_password():
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        password = getpass.getpass("Enter password: ")
        if password == "github.com/afshmari":
            print("Access granted")
            break
        else:
            print(
                f"Access denied. Attempts remaining: {max_attempts - attempt}")
    else:
        print("Maximum number of attempts reached. Aborting.")
        sys.exit(1) 


class BinanceDataFetcher:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def fetch_candlestick_data(self, symbol, interval):
        time.sleep(60)

        candles = self.client.futures_klines(
            symbol=symbol,
            interval=interval,
            limit=150
        )

        candles = candles[:-1]
        previous_candle = candles[-1]  # Previous closed candle

        open_time = datetime.datetime.utcfromtimestamp(
            previous_candle[0] / 1000).strftime('%Y-%m-%d %H:%M')
        # close_time = datetime.datetime.utcfromtimestamp(previous_candle[6] / 1000).strftime('%Y-%m-%d %H:%M')
        # open_price = previous_candle[1]
        # high_price = previous_candle[2]
        # low_price = previous_candle[3]
        # close_price = previous_candle[4]

        print("-----------------------------")
        print("Open Time:", open_time)
        # print("Close Time:  ", close_time)
        # print("Open Price:  ", open_price)
        # print("High Price:  ", high_price)
        # print("Low Price:   ", low_price)
        # print("Close Price: ", close_price)
        print("-----------------------------")
        return candles


class IchimokuSignalGenerator:
    def generate_signal(self, candles):
        high_prices = [float(candle[2]) for candle in reversed(candles)]
        low_prices = [float(candle[3]) for candle in reversed(candles)]
        closing_prices = [float(candle[4]) for candle in reversed(candles)]
        opening_prices = [float(candle[1]) for candle in reversed(candles)]

        tenkan_sen = self.calculate_tenkan_sen(high_prices, low_prices)
        kijun_sen = self.calculate_kijun_sen(high_prices, low_prices)
        tenkan_sen_26_periods_ago = self.calculate_tenkan_sen_26_periods_ago(
            high_prices, low_prices)
        tenkan_sen_52_periods_ago = self.calculate_tenkan_sen_52_periods_ago(
            high_prices, low_prices)
        kijun_sen_26_periods_ago = self.calculate_kijun_sen_26_periods_ago(
            high_prices, low_prices)
        kijun_sen_52_periods_ago = self.calculate_kijun_sen_52_periods_ago(
            high_prices, low_prices)
        senkou_span_a = self.calculate_senkou_span_a(tenkan_sen, kijun_sen)
        senkou_span_a_26 = self.calculate_senkou_span_a(
            tenkan_sen_26_periods_ago, kijun_sen_26_periods_ago)
        senkou_span_a_52 = self.calculate_senkou_span_a(
            tenkan_sen_52_periods_ago, kijun_sen_52_periods_ago)
        senkou_span_b = self.calculate_senkou_span_b(high_prices, low_prices)
        senkou_span_b_26 = self.calculate_senkou_span_b_26(
            high_prices, low_prices)
        senkou_span_b_52 = self.calculate_senkou_span_b_52(
            high_prices, low_prices)

        current_price = closing_prices[0] if closing_prices else None
        current_price_open = opening_prices[0] if opening_prices else None
        lagging_span_26_periods_ago = closing_prices[0] if len(
            closing_prices) >= 26 else None

        pd = senkou_span_b_26

        percentage_difference = abs(
            (current_price - pd) / pd) * 100

        signal = self.determine_signal(tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, senkou_span_a_26, senkou_span_b_26,
                                       senkou_span_a_52, senkou_span_b_52, current_price, current_price_open, lagging_span_26_periods_ago, percentage_difference)

        print("Signal:", signal)
        print("percentage Difference:", percentage_difference)
        print("Current Price Open:", current_price_open)
        print("Current Price:", current_price)
        print("Lagging Span 26 periods ago:", lagging_span_26_periods_ago)
        print("Tenkan-sen:", tenkan_sen)
        print("Kijun-sen:", kijun_sen)
        print("Senkou Span A:", senkou_span_a)
        print("Senkou Span B:", senkou_span_b)
        print("Tenkan-sen 26 periods ago:", tenkan_sen_26_periods_ago)
        print("Kijun-sen 26 periods ago:", kijun_sen_26_periods_ago)
        print("Tenkan-sen 52 periods ago:", tenkan_sen_52_periods_ago)
        print("Kijun-sen 52 periods ago:", kijun_sen_52_periods_ago)
        print("Senkou Span A 26 periods ago:", senkou_span_a_26)
        print("Senkou Span A 52 periods ago:", senkou_span_a_52)
        print("Senkou Span B 26 periods ago:", senkou_span_b_26)
        print("Senkou Span B 52 periods ago:", senkou_span_b_52)
        print("-----------------------------")

        return (high_prices, low_prices, closing_prices, opening_prices, tenkan_sen, kijun_sen, tenkan_sen_26_periods_ago,
                tenkan_sen_52_periods_ago, kijun_sen_26_periods_ago, kijun_sen_52_periods_ago, senkou_span_a,
                senkou_span_a_26, senkou_span_a_52, senkou_span_b, senkou_span_b_26, senkou_span_b_52, current_price,
                current_price_open, lagging_span_26_periods_ago, percentage_difference, signal)

    def calculate_tenkan_sen(self, high_prices, low_prices):
        period9_high = pd.Series(high_prices[:9]).max()
        period9_low = pd.Series(low_prices[:9]).min()
        tenkan_sen = (period9_high + period9_low) / 2
        return tenkan_sen

    def calculate_kijun_sen(self, high_prices, low_prices):
        period26_high = pd.Series(high_prices[:26]).max()
        period26_low = pd.Series(low_prices[:26]).min()
        kijun_sen = (period26_high + period26_low) / 2
        return kijun_sen

    def calculate_tenkan_sen_26_periods_ago(self, high_prices, low_prices):
        period9_high = pd.Series(high_prices[26:35]).max()
        period9_low = pd.Series(low_prices[26:35]).min()
        tenkan_sen_26_periods_ago = (period9_high + period9_low) / 2
        return tenkan_sen_26_periods_ago

    def calculate_tenkan_sen_52_periods_ago(self, high_prices, low_prices):
        period9_high = pd.Series(high_prices[52:61]).max()
        period9_low = pd.Series(low_prices[52:61]).min()
        tenkan_sen_52_periods_ago = (period9_high + period9_low) / 2
        return tenkan_sen_52_periods_ago

    def calculate_kijun_sen_26_periods_ago(self, high_prices, low_prices):
        period26_high = pd.Series(high_prices[26:52]).max()
        period26_low = pd.Series(low_prices[26:52]).min()
        kijun_sen_26_periods_ago = (period26_high + period26_low) / 2
        return kijun_sen_26_periods_ago

    def calculate_kijun_sen_52_periods_ago(self, high_prices, low_prices):
        period26_high = pd.Series(high_prices[52:78]).max()
        period26_low = pd.Series(low_prices[52:78]).min()
        kijun_sen_52_periods_ago = (period26_high + period26_low) / 2
        return kijun_sen_52_periods_ago

    def calculate_senkou_span_a(self, tenkan_sen, kijun_sen):
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2)
        return senkou_span_a

    def calculate_senkou_span_a_26(self, tenkan_sen_26_periods_ago, kijun_sen_26_periods_ago):
        senkou_span_a_26 = ((tenkan_sen_26_periods_ago +
                            kijun_sen_26_periods_ago) / 2)
        return senkou_span_a_26

    def calculate_senkou_span_a_52(self, tenkan_sen_52_periods_ago, kijun_sen_52_periods_ago):
        senkou_span_a_52 = ((tenkan_sen_52_periods_ago +
                            kijun_sen_52_periods_ago) / 2)
        return senkou_span_a_52

    def calculate_senkou_span_b(self, high_prices, low_prices):
        period52_high = pd.Series(high_prices[:52]).max()
        period52_low = pd.Series(low_prices[:52]).min()
        senkou_span_b = ((period52_high + period52_low) / 2)
        return senkou_span_b

    def calculate_senkou_span_b_26(self, high_prices, low_prices):
        period52_high = pd.Series(high_prices[26:78]).max()
        period52_low = pd.Series(low_prices[26:78]).min()
        senkou_span_b_26 = ((period52_high + period52_low) / 2)
        return senkou_span_b_26

    def calculate_senkou_span_b_52(self, high_prices, low_prices):
        period52_high = pd.Series(high_prices[52:104]).max()
        period52_low = pd.Series(low_prices[52:104]).min()
        senkou_span_b_52 = ((period52_high + period52_low) / 2)
        return senkou_span_b_52

    def determine_signal(self, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, senkou_span_a_26, senkou_span_b_26, senkou_span_a_52, senkou_span_b_52, current_price, current_price_open, lagging_span_26_periods_ago, percentage_difference):
        if percentage_difference <= 0.2 or percentage_difference >= 2:
            signal = "No signal"
        else:
            if (
                current_price > current_price_open and
                tenkan_sen > kijun_sen and
                senkou_span_a > senkou_span_b and
                lagging_span_26_periods_ago > senkou_span_a_52 and
                lagging_span_26_periods_ago > senkou_span_b_52 and
                current_price > senkou_span_a_26 and
                current_price > senkou_span_b_26
            ):
                signal = "Buy"
            elif (
                current_price < current_price_open and
                tenkan_sen < kijun_sen and
                senkou_span_a < senkou_span_b and
                lagging_span_26_periods_ago < senkou_span_a_52 and
                lagging_span_26_periods_ago < senkou_span_b_52 and
                current_price < senkou_span_a_26 and
                current_price < senkou_span_b_26
            ):
                signal = "Sell"
            else:
                signal = "No signal"

        return signal


class BinanceFuturesOrderPlacer:

    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_decimal_places(self, symbol):
        symbol_info = self.client.futures_exchange_info()
        for symbol_data in symbol_info['symbols']:
            if symbol_data['symbol'] == symbol:
                filters = symbol_data['filters']
                price_filter = next(
                    (f for f in filters if f['filterType'] == 'PRICE_FILTER'), None)
                tick_size = float(price_filter['tickSize'])
                decimal_places = abs(int(math.log10(tick_size)))
                return decimal_places
        raise ValueError(f"Symbol {symbol} not found in exchange info.")

    def adjust_leverage(self, symbol, leverage):
        leverage_params = {
            "symbol": symbol,
            "leverage": leverage
        }

        try:
            result = self.client.futures_change_leverage(**leverage_params)
            return result
        except Exception as e:
            print("An error occurred while adjusting leverage:", str(e))
            print("-----------------------------")
            return None

    def format_price(self, price, decimal_places):
        formatted_price = f"{price:.{decimal_places}f}"
        return formatted_price

    def place_order(self, symbol, quantity, side, stop_loss, take_profit, leverage):
        result = self.adjust_leverage(symbol, leverage)
        if result is None:
            print("Failed to adjust leverage. Aborting order placement.")
            return None

        decimal_places = self.get_decimal_places(symbol)
        formatted_stop_loss = self.format_price(stop_loss, decimal_places)
        formatted_take_profit = self.format_price(take_profit, decimal_places)

        order_params = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": "MARKET",
        }

        try:
            order = self.client.futures_create_order(**order_params)
            print("Market order placed")

            stop_loss_order_params = {
                "symbol": symbol,
                "side": Client.SIDE_SELL if side == Client.SIDE_BUY else Client.SIDE_BUY,
                "quantity": quantity,
                "type": "STOP_MARKET",
                "stopPrice": formatted_stop_loss,
                "closePosition": True,
            }
            stop_loss_order = self.client.futures_create_order(
                **stop_loss_order_params)
            print("Stop loss order placed")

            take_profit_order_params = {
                "symbol": symbol,
                "side": Client.SIDE_SELL if side == Client.SIDE_BUY else Client.SIDE_BUY,
                "quantity": quantity,
                "type": "TAKE_PROFIT_MARKET",
                "stopPrice": formatted_take_profit,
                "closePosition": True,
            }
            take_profit_order = self.client.futures_create_order(
                **take_profit_order_params)
            print("Take profit order placed")

            while True:
                stop_loss_order = self.client.futures_get_order(
                    symbol=symbol, orderId=stop_loss_order["orderId"])
                take_profit_order = self.client.futures_get_order(
                    symbol=symbol, orderId=take_profit_order["orderId"])

                if stop_loss_order["status"] == "FILLED":
                    print("Stop loss order filled. Cancelling take profit order.")
                    self.client.futures_cancel_order(
                        symbol=symbol, orderId=take_profit_order["orderId"])
                    break
                elif take_profit_order["status"] == "FILLED":
                    print("Take profit order filled. Cancelling stop loss order.")
                    self.client.futures_cancel_order(
                        symbol=symbol, orderId=stop_loss_order["orderId"])
                    break

                time.sleep(15) 
            return order
        except Exception as e:
            print("An error occurred while placing the order:", str(e))
            print("-----------------------------")
            return None


class BinancePositionChecker:
    @staticmethod
    def check_open_position(api_key, api_secret, symbol):
        client = Client(api_key, api_secret)

        try:
            positions = client.futures_position_information()
            for position in positions:
                if position['symbol'] == symbol and position['positionAmt'] != '0':
                    return True
            return False
        except Exception as e:
            print("An error occurred while checking open positions:", str(e))
            print("-----------------------------")

            return False


check_password()
symbol = input("Enter the trading pair symbol (e.g., BTCUSDT): ")
amount_usd = float(input("Enter the amount in USD: "))
leverage = int(input("Enter the desired leverage: "))
timeframe = input("Enter the desired timeframe (e.g., 15m, 1h, 4h): ")
api_key = input("Enter your Binance API key: ")
api_secret = input("Enter your Binance API secret: ")
risk_reward = int(input("Enter the desired risk reward ratio: "))

symbol = symbol.upper()
interval = f"{timeframe}m"  # Assuming minutes

recv_window = 60000
exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": api_secret,
    "options": {
        "recvWindow": recv_window
    }
})

fetcher = BinanceDataFetcher(api_key, api_secret)
order_placer = BinanceFuturesOrderPlacer(api_key, api_secret)

while True:

    try:
        candles = fetcher.fetch_candlestick_data(symbol, interval)
    except Exception as e:
        print("An error occurred while fetching candlestick data:", str(e))
        print("-----------------------------")

    signal_generator = IchimokuSignalGenerator()
    (high_prices, low_prices, closing_prices, opening_prices, tenkan_sen, kijun_sen, tenkan_sen_26_periods_ago,
     tenkan_sen_52_periods_ago, kijun_sen_26_periods_ago, kijun_sen_52_periods_ago, senkou_span_a,
     senkou_span_a_26, senkou_span_a_52, senkou_span_b, senkou_span_b_26, senkou_span_b_52, current_price,
     current_price_open, lagging_span_26_periods_ago, percentage_difference, signal) = signal_generator.generate_signal(candles)

    if signal == "Buy" or signal == "Sell":
        position_checker = BinancePositionChecker()
        has_open_position = False
        try:
            has_open_position = position_checker.check_open_position(
                api_key, api_secret, symbol.upper())
            if has_open_position == True:
                print(
                    f"Position Status: There is an open position for {symbol}. Skipping order placement.")
                print("-----------------------------")
            elif has_open_position == False:
                print("Position Status: No positions")
                print("-----------------------------")

        except Exception as e:
            print("An error occurred while checking open positions:", str(e))
            print("-----------------------------")

        if has_open_position == False:
            quantity = amount_usd / current_price

            if signal == "Buy":
                side = "BUY"
            elif signal == "Sell":
                side = "SELL"
            else:
                continue 

            if signal == "Buy":
                TPSLBase = min(senkou_span_b_26, kijun_sen, senkou_span_a_26)

                TPSLBase_percentage = abs(
                    current_price - TPSLBase) / abs(TPSLBase)
                stop_loss = float(TPSLBase)
                take_profit = float(
                    TPSLBase * (1 + (risk_reward + 1) * TPSLBase_percentage))
            else:
                TPSLBase = max(senkou_span_b_26, kijun_sen, senkou_span_a_26)
                TPSLBase_percentage = abs(
                    current_price - TPSLBase) / abs(TPSLBase)
                stop_loss = float(TPSLBase)
                take_profit = float(
                    TPSLBase * (1 - (risk_reward + 1) * TPSLBase_percentage))

            quantity = math.floor(amount_usd / current_price)

            try:
                order = order_placer.place_order(
                    symbol, quantity, side, stop_loss, take_profit, leverage)

            except Exception as e:
                print("An error occurred while placing order:", str(e))
                print("-----------------------------")
    else:
        continue
