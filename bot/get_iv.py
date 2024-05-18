import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import numpy as np
import seaborn as sns
import os
import time
from api.bybit.bybit import Bybit
from bot.frame_to_img import render_mpl_table


def near_future_expiry() -> datetime:
    now = datetime.now()
    if now >= datetime(now.year, now.month, now.day, 17, 0, 0):
        next_day = now+timedelta(days=1)
        expiry_1d = datetime(next_day.year, next_day.month, next_day.day, 17, 0, 0)
    else:
        expiry_1d = datetime(now.year, now.month, now.day, 17, 0, 0)
    return expiry_1d


def spot_ohlc(symbol: str = 'BTCUSDT', interval: str = '60'):
    ### SpotPrice
    params = {'category': 'linear', 'symbol': symbol, 'interval': interval,
              'start': str(int((datetime.now()+timedelta(days=-30)).timestamp()))+'000',
              'end': str(int((datetime.now().timestamp())))+'000',
              'limit': '1000'}
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    spot_prices = bybit.send_request('GET', 'public', '/v5/market/mark-price-kline', params).json().get('result').get('list')

    spot_prices = pd.DataFrame(spot_prices)
    spot_prices.columns = ['datetime', 'open', 'high', 'low', 'last']
    spot_prices['datetime'] = spot_prices['datetime'].str.slice(0,10).apply(lambda x: datetime.fromtimestamp(int(x)))
    spot_prices[['open', 'high', 'low', 'last']] = spot_prices[['open', 'high', 'low', 'last']].astype(float)

    return spot_prices


def last_iv(basecoin: str = 'BTC', n_day: int = 0, iv_fig_path: str = 'iv.png', price_fig_path: str = 'price.png', table_fig_path: str = 'table.png'):
    spot_prices = spot_ohlc(symbol=f'''{basecoin}USDT''', interval='3').head(20*24).assign(Return = lambda df: df['last'].pct_change()) # 1Day
    realized_vol = np.sqrt(spot_prices['Return'].pipe(lambda x: x*x).sum()*365)

    ### OptionPriceからIV計算

    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    expiry = near_future_expiry() + timedelta(days=n_day)
    tickers = (
        pd.DataFrame(bybit.send_request('GET',
                                        'public',
                                        target_path='/v5/market/tickers',
                                        params={'category':'option', 'baseCoin': basecoin, 'expDate': expiry.strftime('%d%B%y').upper()})
                     .json().get('result').get('list'))
            .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
            .reset_index(drop=True)
    )

    price_list = []
    for ticker in tickers['symbol'].drop_duplicates().tolist():
        params = {'category': 'option', 'symbol': ticker, 'limit': '1'}
        response = requests.get(url='https://api.bybit.com/v5/market/recent-trade', params=params)
        try:
            execution = response.json().get('result').get('list')
            if len(execution)>0: price_list.append(pd.DataFrame(execution))
        except:
            pass
        time.sleep(np.random.exponential(0.1,1)[0])

    prices = (
        pd.concat(price_list)
            .rename(columns = {'time': 'datetime'})
            .reset_index(drop=True)
            .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
            .assign(pc = lambda df: df['symbol'].str.slice(-1))
            .assign(strike = lambda df: df['K'])
    )
    prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv', 'K']] = prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv', 'K']].astype(float)
    prices['datetime'] = prices['datetime'].str.slice(0,10).astype(int).apply(lambda x: datetime.fromtimestamp(x))

    prices = (
        prices
            .assign(expire = expiry)
            .assign(dt = lambda df: (df['expire']-df['datetime']).dt.total_seconds())
    )
    # Bybit IV
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(6,4))
    sns.lineplot(data=prices.assign(pc = lambda df: df['pc']+'-'+df['symbol'].apply(lambda x: x.split('-')[1])),
                 x='strike', y='iv', hue='pc', marker='o', ax=ax)
    ax.set_ylabel('Implied Volatility')
    ax.hlines(realized_vol, ax.get_xlim()[0], ax.get_xlim()[1])
    ax.text(ax.get_xlim()[0], realized_vol+0.05, 'Realized Volatility?', color='black')

    plt.savefig(iv_fig_path)

    # Bybit Call Price
    fig, ax = plt.subplots(figsize=(6,4))
    sns.set_style("whitegrid")
    sns.lineplot(data=prices.assign(pc = lambda df: df['pc']+'-'+df['symbol'].apply(lambda x: x.split('-')[1])),
                 x='strike', y='price', hue='pc', marker='o')
    plt.savefig(price_fig_path)

    # Bybit Table
    op_spot = prices.assign(datetime = lambda df: df['datetime'].dt.round('min'))
    op_spot = pd.merge(op_spot, spot_prices, on='datetime')
    _img = (
        op_spot
            .sort_values('iv', ascending=False)[['datetime', 'symbol', 'pc', 'price', 'size', 'strike', 'iv', 'side', 'last']]
            .rename(columns = {'last': 'Spot'}).head(4)
    )
    _img.columns = [_col.upper() for _col in _img.columns]
    fig, ax = render_mpl_table(_img, col_width=2)
    plt.savefig(table_fig_path)

    return op_spot


def askbid_iv(basecoin: str = 'BTC', n_day: int = 0, askbid_fig_path: str = 'askbidiv.png'):
    spot_prices = spot_ohlc(symbol=basecoin + 'USDT', interval='3').head(20*24).assign(Return = lambda df: df['last'].pct_change()) # 1Day
    realized_vol = np.sqrt(spot_prices['Return'].pipe(lambda x: x*x).sum()*365)

    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    expiry = near_future_expiry() + timedelta(days=n_day)
    op_tickers = (
        pd.DataFrame(bybit.send_request('GET',
                                        'public',
                                        target_path='/v5/market/tickers',
                                        params={'category':'option', 'baseCoin': basecoin, 'expDate': expiry.strftime('%d%B%y').upper()})
                     .json().get('result').get('list'))
        .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
        .pipe(lambda df: df[df['symbol'].str.slice(-1)=='P'])
        .reset_index(drop=True)
    )
    bid = op_tickers[['symbol', 'bid1Price', 'bid1Size', 'bid1Iv', 'indexPrice', 'K']].assign(AskBid = 'Bid')
    ask = op_tickers[['symbol', 'ask1Price', 'ask1Size', 'ask1Iv', 'indexPrice', 'K']].assign(AskBid = 'Ask')
    bid.columns = ['Symbol', 'Price', 'Size', 'Iv', 'IndexPrice', 'K', 'AskBid']
    ask.columns = ['Symbol', 'Price', 'Size', 'Iv', 'IndexPrice', 'K', 'AskBid']
    askbid = pd.concat([ask, bid]).reset_index(drop=True)
    askbid[['Price', 'Size', 'Iv', 'IndexPrice', 'K']] = askbid[['Price', 'Size', 'Iv', 'IndexPrice', 'K']].astype(float)

    sns.set_style('whitegrid')
    fig, ax = plt.subplots(figsize=(6,4))
    sns.scatterplot(data=askbid, x='K', y='Iv', hue='AskBid', marker='o', size='Size', ax=ax)
    ax.hlines(realized_vol, ax.get_xlim()[0], ax.get_xlim()[1])
    ax.text(ax.get_xlim()[0], realized_vol+0.05, 'Realized Volatility?', color='black')
    plt.savefig(askbid_fig_path)

    return askbid


if __name__ == '__main__':
    print(near_future_expiry())
    print(spot_ohlc())
    print(last_iv())
    print(askbid_iv())