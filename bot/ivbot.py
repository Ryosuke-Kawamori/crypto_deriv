import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

import scipy.stats as st
import scipy
import io
import seaborn as sns
from bot.frame_to_img import render_mpl_table

def get_iv():

    ### SpotPrice
    params = {'category': 'linear', 'symbol': 'BTCUSDT', 'interval': '1',
              'start': str(int((datetime.now()+timedelta(days=-1)).timestamp()))+'000',
              'end': str(int((datetime.now().timestamp())))+'000',
              'limit': 10000}
    response = requests.get(url='https://api.bybit.com/v5/market/mark-price-kline', params=params)
    response.json()
    spot_prices = response.json().get('result').get('list')

    spot_prices = pd.DataFrame(spot_prices)
    spot_prices.columns = ['datetime', 'open', 'high', 'low', 'last']
    spot_prices['datetime'] = spot_prices['datetime'].str.slice(0,10).apply(lambda x: datetime.fromtimestamp(int(x)))
    spot_prices[['open', 'high', 'low', 'last']] = spot_prices[['open', 'high', 'low', 'last']].astype(float)
    spot_prices.head(5)
    spot = spot_prices.iloc[0,4]

    ### OptionPriceからIV計算
    _today = date.today()
    prices = pd.DataFrame(columns = ['symbol', 'size', 'price', 'miv', 'iv', 'datetime', 'strike', 'pc', 'side'])

    for k in [round(spot/250)*250+250*i for i in range(-100,100)]:
        params = {'category': 'option', 'symbol': f'''BTC-{_today.day}{_today.strftime('%b').upper()}{str(_today.year)[2:4]}-{k}-C''', 'limit': '1'}
        response = requests.get(url='https://api.bybit.com/v5/market/recent-trade', params=params)
        try:
            execution = response.json().get('result').get('list')[0]
            price = float(execution.get('price'))
            size = float(execution.get('size'))
            symbol = execution.get('symbol')
            miv = float(execution.get('mIv'))
            iv = float(execution.get('iv'))
            dt = datetime.fromtimestamp(int(execution.get('time')[0:10]))
            strike = k
            side = execution.get('side')
            prices = pd.concat([prices,
                                pd.Series([symbol, size, price, miv, iv, dt, strike, 'Call', side],
                                           index=['symbol', 'size', 'price', 'miv', 'iv', 'datetime', 'strike', 'pc', 'side']).to_frame().T]
                              )
        except:
            pass

    for k in [round(spot/250)*250+250*i for i in range(-100,20)]:
        params = {'category': 'option', 'symbol': f'''BTC-{_today.day}{_today.strftime('%b').upper()}{str(_today.year)[2:4]}-{k}-P''', 'limit': '1'}
        response = requests.get(url='https://api.bybit.com/v5/market/recent-trade', params=params)
        try:
            execution = response.json().get('result').get('list')[0]
            price = float(execution.get('price'))
            size = float(execution.get('size'))
            symbol = execution.get('symbol')
            miv = float(execution.get('mIv'))
            iv = float(execution.get('iv'))
            dt = datetime.fromtimestamp(int(execution.get('time')[0:10]))
            strike = k
            side = execution.get('side')
            prices = pd.concat([prices,
                                pd.Series([symbol, size, price, miv, iv, dt, strike, 'Put', side],
                                           index=['symbol', 'size', 'price', 'miv', 'iv', 'datetime', 'strike', 'pc', 'side']).to_frame().T]
                              )
        except:
            pass

    prices = (
        prices
            .assign(expire = lambda df: datetime(_today.year,_today.month,_today.day,0,0,0))
            .assign(dt = lambda df: (df['expire']-df['datetime']).dt.seconds)
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
    fig, ax = render_mpl_table(_img, col_width=2)
    _img = (op_spot
        .sort_values('iv', ascending=False)[['datetime', 'symbol', 'pc', 'price', 'size', 'symbol', 'strike', 'iv', 'side', 'last']]
        .rename(columns = {'last': 'Spot'}).head(4)
        )
    _img.columns = [_col.upper() for _col in _img.columns]
    plt.savefig('table.png')

    return op_spot


import discord
import os
# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.getenv('TOKEN')

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('Login')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    # IV
    if message.content == '/iv':
        vol = get_iv()
        await message.channel.send(file=discord.File('price.png'))
        await message.channel.send(file=discord.File('iv.png'))
        await message.channel.send(vol.sort_values('iv', ascending=False)[['datetime', 'symbol', 'pc', 'price', 'size', 'symbol', 'strike', 'iv', 'side', 'last']].rename(columns = {'last': 'Spot'}).head(4).to_markdown())

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)