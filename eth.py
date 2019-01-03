import pandas as pd
import requests
from pandas import DataFrame

from indicators import SuperTrend

"""
OKEx: ETH-USDT
Api:  https://www.okex.com/api/spot/v3/instruments/eth_usdt/candles
请求参数
参数                  类型              描述
start	            string	        [非必填]开始时间(ISO 8601标准)
end	                string	        [非必填]结束时间(ISO 8601标准)
granularity	        integer	        [非必填]以秒来计量的时间粒度
instrument_id	    string	        [必填]币对
"""
PAIR = 'eth_usdt'
PERIOD = 3600 * 2
pd.set_option('display.max_rows', None)
USDT_BALANCE = 3000
COIN_BALANCE = 0
TAX = 0.02


def get_candle_df():
    r = requests.get("https://www.okex.com/api/spot/v3/instruments/{}/candles?granularity={}".format(PAIR, PERIOD))
    if r.status_code != 200:
        return None
    sticks = []
    for item in r.json():
        stick = [item['time'], float(item['open']), float(item['high']), float(item['low']), float(item['close']),
                 float(item['volume'])]
        sticks.insert(0, stick)
    return DataFrame(sticks, columns=['date', 'open', 'high', 'low', 'close', 'volume'])


def buy(price):
    global USDT_BALANCE, COIN_BALANCE
    volume = USDT_BALANCE / price * (1 - TAX)
    COIN_BALANCE += volume
    USDT_BALANCE = 0


def sell(price):
    global USDT_BALANCE, COIN_BALANCE
    amount = COIN_BALANCE * price * (1 - TAX)
    USDT_BALANCE += amount
    COIN_BALANCE = 0


def summary(price):
    print("END:   USDT: {}, COIN: {}, USDT_ALL: {}".format(USDT_BALANCE, COIN_BALANCE, COIN_BALANCE * price))


def run():
    df = get_candle_df()
    period = 7
    multi = 3
    # st = 'ST_{}_{}'.format(period, multi)
    stx = 'STX_{}_{}'.format(period, multi)
    r = SuperTrend(df, period, multi)
    print(r.to_string())
    for idx, row in r.iterrows():
        if idx < period + 1:
            continue
        if row[stx] != r.loc[idx - 1, stx]:
            if row[stx] == 'up':
                direction = 'buy'
                buy(row['close'] + 0.5)
            if row[stx] == 'down':
                direction = 'sell'
                sell(row['close'] - 0.5)
            print('{} {} at {}'.format(row['date'], direction, row['close']))
    price_now = r.loc[len(r) - 1, 'close']
    print('price now: {}'.format(price_now))
    summary(price_now)


if __name__ == '__main__':
    run()
