import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import numpy as np
import seaborn as sns
import os
import time
from api.bybit.bybit import Bybit


def spot_ohlc(symbol: str = 'BTCUSDT', interval: str = '60', limit: str='1000'):
    ### SpotPrice
    params = {'category': 'linear', 'symbol': symbol, 'interval': interval,
              'start': str(int((datetime.now()+timedelta(days=-1000)).timestamp()))+'000',
              'end': str(int((datetime.now().timestamp())))+'000',
              'limit': limit}
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    spot_prices = bybit.send_request('GET', 'public', '/v5/market/mark-price-kline', params).json().get('result').get('list')

    spot_prices = pd.DataFrame(spot_prices)
    spot_prices.columns = ['datetime', 'open', 'high', 'low', 'last']
    spot_prices['datetime'] = spot_prices['datetime'].str.slice(0,10).apply(lambda x: datetime.fromtimestamp(int(x)))
    spot_prices[['open', 'high', 'low', 'last']] = spot_prices[['open', 'high', 'low', 'last']].astype(float)

    return spot_prices