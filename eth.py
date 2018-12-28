import pandas as pd
import requests
from pandas import DataFrame

from indicators import SuperTrend

"""
OKRx: ETH-USDT
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


def run():
    df = get_candle_df()
    r = SuperTrend(df, 12, 2, ohlc=['open', 'high', 'low', 'close'])
    print(r.to_string())


if __name__ == '__main__':
    run()
