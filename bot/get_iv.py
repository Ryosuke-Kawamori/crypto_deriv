import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

import seaborn as sns
from bot.frame_to_img import render_mpl_table


def get_near_future_expiry() -> datetime:
    now = datetime.now()
    if now >= datetime(now.year, now.month, now.day, 10, 0, 0):
        _next_day = now+timedelta(days=1)
        expiry_1d = datetime(_next_day.year, _next_day.month, _next_day.day, 10, 0, 0)
    else:
        expiry_1d = datetime(now.year, now.month, now.day, 10, 0, 0)
    return expiry_1d


def get_last_index_trade():
    ### SpotPrice
    params = {'category': 'linear', 'symbol': 'BTCUSDT', 'interval': '1',
              'start': str(int((datetime.now()+timedelta(days=-1)).timestamp()))+'000',
              'end': str(int((datetime.now().timestamp())))+'000',
              'limit': 1000}
    response = requests.get(url='https://api.bybit.com/v5/market/mark-price-kline', params=params)
    response.json()
    spot_prices = response.json().get('result').get('list')

    spot_prices = pd.DataFrame(spot_prices)
    spot_prices.columns = ['datetime', 'open', 'high', 'low', 'last']
    spot_prices['datetime'] = spot_prices['datetime'].str.slice(0,10).apply(lambda x: datetime.fromtimestamp(int(x)))
    spot_prices[['open', 'high', 'low', 'last']] = spot_prices[['open', 'high', 'low', 'last']].astype(float)

    return spot_prices


def get_last_iv():
    spot_prices = get_last_index_trade()
    spot = spot_prices.iloc[0,4]

    ### OptionPriceからIV計算
    _today = get_near_future_expiry()

    price_list = []

    for k in [round(spot/250)*250+250*i for i in range(-10,100)]:
        params = {'category': 'option', 'symbol': f'''BTC-{_today.day}{_today.strftime('%b').upper()}{str(_today.year)[2:4]}-{k}-C''', 'limit': '1'}
        response = requests.get(url='https://api.bybit.com/v5/market/recent-trade', params=params)
        try:
            execution = response.json().get('result').get('list')
            price_list.append(pd.DataFrame(execution).assign(pc='Call').assign(strike=k))
        except:
            pass

    for k in [round(spot/250)*250+250*i for i in range(-100,10)]:
        params = {'category': 'option', 'symbol': f'''BTC-{_today.day}{_today.strftime('%b').upper()}{str(_today.year)[2:4]}-{k}-P''', 'limit': '1'}
        response = requests.get(url='https://api.bybit.com/v5/market/recent-trade', params=params)
        try:
            execution = response.json().get('result').get('list')
            price_list.append(pd.DataFrame(execution).assign(pc='Put').assign(strike=k))
        except:
            pass

    prices = pd.concat(price_list).rename(columns = {'time': 'datetime'})
    prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv']] = prices[['price', 'size', 'mP', 'iP', 'mIv', 'iv']].astype(float)
    prices['datetime'] = prices['datetime'].str.slice(0,10).astype(int).apply(lambda x: datetime.fromtimestamp(x))

    prices = (
        prices
            .assign(expire = lambda df: datetime(_today.year,_today.month,_today.day,0,0,0))
            .assign(dt = lambda df: (df['expire']-df['datetime']).dt.total_seconds())
    )
    # Bybit IV
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(6,4))
    sns.lineplot(data=prices.assign(pc = lambda df: df['pc']+'-'+df['symbol'].apply(lambda x: x.split('-')[1])),
                 x='strike', y='iv', hue='pc', marker='o', ax=ax)
    ax.set_ylabel('Implied Volatility')
    plt.savefig('iv.png')

    # Bybit Call Price
    fig, ax = plt.subplots(figsize=(6,4))
    sns.set_style("whitegrid")
    sns.lineplot(data=prices.assign(pc = lambda df: df['pc']+'-'+df['symbol'].apply(lambda x: x.split('-')[1])),
                 x='strike', y='price', hue='pc', marker='o')
    plt.savefig('price.png')

    # Bybit Table
    op_spot = prices.assign(datetime = lambda df: df['datetime'].dt.round('min'))
    op_spot = pd.merge(op_spot, spot_prices, on='datetime')
    _img = (
        op_spot
            .sort_values('iv', ascending=False)[['datetime', 'symbol', 'pc', 'price', 'size', 'symbol', 'strike', 'iv', 'side', 'last']]
            .rename(columns = {'last': 'Spot'}).head(4)
    )
    _img.columns = [_col.upper() for _col in _img.columns]
    fig, ax = render_mpl_table(_img, col_width=2)
    plt.savefig('table.png')

    return op_spot


def get_askbid_iv():
    ticker_list = []
    S = get_last_index_trade().iloc[0,4]
    expiry_1d = get_near_future_expiry()
    for k in [round(S/250)*250+250*i for i in range(-100,20)]:
        params = {'category': 'option', 'symbol': f'''BTC-{expiry_1d.day}{expiry_1d.strftime('%b').upper()}{str(expiry_1d.year)[2:4]}-{k}-P'''}
        response = requests.get(url='https://api.bybit.com/v5/market/tickers', params=params)
        if len(response.json().get('result').get('list'))>0:
            ticker_list.append(pd.DataFrame(response.json().get('result').get('list')))

    op_tickers = (
        pd.concat(ticker_list).reset_index()[['symbol', 'bid1Price', 'bid1Size', 'bid1Iv',  'ask1Price', 'ask1Size', 'ask1Iv', 'indexPrice']]
            .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
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
    plt.savefig('askbidiv.png')

    return askbid