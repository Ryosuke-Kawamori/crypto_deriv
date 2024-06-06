import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import seaborn as sns

import os
import pandas as pd

from api.bybit.bybit import Bybit
from api.bybit.market_data import spot_ohlc
from common.black_schoels import gamma, delta, vega


def gamma_exposure(basecoin: str = 'BTC', gamma_type: str = 'general', plt_save_path: str = 'gamma_exposure.png'):
    params = {'category': 'option',  'baseCoin': basecoin, 'limit': '1000'}
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    last_prices = bybit.send_request('GET', 'public', '/v5/market/recent-trade', params).json().get('result').get('list')
    last_prices = pd.DataFrame(last_prices)
    last_prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv']] = last_prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv']].astype(float)
    last_prices['time'] = last_prices['time'].str.slice(0,10).astype(int).map(lambda x: datetime.fromtimestamp(x))
    spot = spot_ohlc(symbol = basecoin+'USDT', interval='1', limit=1).head(1)['last'].squeeze()
    hedge_delta_list = []

    # Dealer Gamma for each Spot
    for i in range(-int(spot*0.1), int(spot*0.1), 100):
        _S = spot + i
        hedge_delta = (
            last_prices.pipe(lambda df: df[df['iv']!=0])
                .assign(EXPIRY = lambda df: df['symbol'].apply(lambda x: x.split('-')[1]))
                .assign(EXPIRY = lambda df: df['EXPIRY'].apply(lambda x: datetime.strptime(x, '%d%b%y')))
                .assign(EXPIRY = lambda df: df['EXPIRY'].apply(lambda x: datetime(x.year, x.month, x.day, 17, 0, 0)))
                .assign(T = lambda df: (df['EXPIRY'].apply(lambda x: x - datetime.now()).dt.total_seconds()))
                .assign(DT = lambda df: df['T']/(365*24*60*60))
                .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
                .assign(CP = lambda df: df['symbol'].apply(lambda x: x.split('-')[3]))
                .assign(DELTA = lambda df: df.apply(lambda x: delta(S=_S, K=x['K'], r=0, vol=x['iv'], dt=x['DT'], cp=x['CP']), axis=1))
                .assign(GAMMA = lambda df: df.apply(lambda x: gamma(S=_S, K=x['K'], r=0, vol=x['iv'], dt=x['DT']), axis=1))
                .assign(HDELTA = lambda df: _S*0.01*df['GAMMA']*_S*df['size'])
                .assign(S = _S)
        )
        hedge_delta_list.append(hedge_delta)

    # Plot Gamma Exposure
    if gamma_type == 'take':
        market_gamma = pd.concat(hedge_delta_list).reset_index(drop=True).assign(HDELTA = lambda df: df['HDELTA'].mask(df['side']=='Buy', -df['HDELTA']))
    else:
        market_gamma = pd.concat(hedge_delta_list).reset_index(drop=True).assign(HDELTA = lambda df: df['HDELTA'].mask(df['CP']=='P', -df['HDELTA']))

    market_gamma = (
        market_gamma
        .assign(CP_EXPIRY = lambda df: df['CP'] + '-' + df['EXPIRY'].dt.strftime('%y%b%d') + '-' +df['K'].astype(str) + '-' + df['side'])
        .groupby(['S', 'CP_EXPIRY'])[['HDELTA']].sum().reset_index()
        .set_index(['S', 'CP_EXPIRY'])['HDELTA'].unstack()
        .assign(Aggregated = lambda df: df.sum(axis=1)).stack().rename('DELTA').reset_index()
    )
    important_cp = (
        market_gamma
            .pipe(lambda df: df[df['CP_EXPIRY']!='Aggregated'])
            .assign(DELTA = lambda df: df['DELTA'].abs())
            .groupby(['CP_EXPIRY'])['DELTA'].max()
            .sort_values().reset_index()
            .tail(4)
        ['CP_EXPIRY'].tolist()
    )

    sns.set_style('whitegrid')
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=market_gamma.pipe(lambda df: df[df['CP_EXPIRY'].isin(important_cp)]), x='S', y='DELTA', hue='CP_EXPIRY', ax=ax)
    sns.lineplot(data=market_gamma.pipe(lambda df: df[df['CP_EXPIRY']=='Aggregated']), x='S', y='DELTA', hue='CP_EXPIRY', linewidth=5, ax=ax)
    ax.set_xlabel('Strike')
    ax.set_ylabel(f'''Gamma Exposure (Dollar/1% Spot Move)\n Trades From {last_prices.tail(1)['time'].squeeze()}''')
    plt.savefig(plt_save_path)