import time
from datetime import datetime
from math import ceil

import pandas as pd
import pytz
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
PERIOD = 3600
pd.set_option('display.max_rows', None)
USDT_BALANCE = 3000
COIN_BALANCE = 0
TAX = 0.02
KLINE_START = '2018-10-15T00:00:00.000Z'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'


def get_candle_df():
    start = int(datetime.strptime(KLINE_START, TIME_FORMAT).timestamp() - time.altzone)
    end = int(time.time() // PERIOD * PERIOD)
    _df = []
    length = ceil((end - start) / (PERIOD * 200))
    for idx, ts in enumerate(range(start, end, PERIOD * 200)):
        formatted_time = datetime.fromtimestamp(ts, pytz.UTC).strftime(TIME_FORMAT)
        end_formatted_time = datetime.fromtimestamp(ts + PERIOD * 200, pytz.UTC).strftime(TIME_FORMAT)
        print('\rGet data: {:.2f}%'.format((idx + 1) / length * 100), end='')
        r = requests.get(
            "https://www.okex.com/api/spot/v3/instruments/{}/candles?granularity={}&start={}&end={}".format(
                PAIR, PERIOD, formatted_time, end_formatted_time))
        if r.status_code != 200:
            return None
        sticks = []
        for item in r.json():
            stick = [item['time'], float(item['open']), float(item['high']), float(item['low']), float(item['close']),
                     float(item['volume'])]
            sticks.insert(0, stick)
        _temp = DataFrame(sticks, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        _df.append(_temp)

    return pd.concat(_df, ignore_index=True)


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


def run_super_trend():
    df = get_candle_df()
    period, multi = 11, 6
    r = SuperTrend(df, period, multi)
    target = r.loc[len(r) - 1, 'ST_{}_{}'.format(period, multi)]
    target_d = r.loc[len(r) - 1, 'STX_{}_{}'.format(period, multi)]
    print("\n参数: {}, {}: 现价: {}，目标: {}, 方向: {}".format(period, multi, r.loc[len(r) - 1, 'close'], target, target_d))
    period, multi = 7, 3
    r = SuperTrend(df, period, multi)
    target = r.loc[len(r) - 1, 'ST_{}_{}'.format(period, multi)]
    target_d = r.loc[len(r) - 1, 'STX_{}_{}'.format(period, multi)]
    print("参数: {}, {}: 现价: {}，目标: {}, 方向: {}".format(period, multi, r.loc[len(r) - 1, 'close'], target, target_d))


def sp_trade(r, period, multi):
    stx = 'STX_{}_{}'.format(period, multi)
    direction = None
    for idx, row in r.iterrows():
        if idx <= period + 1:
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
    run_super_trend()
