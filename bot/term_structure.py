from datetime import datetime, date, timedelta
import seaborn as sns
import os
import pandas as pd
import matplotlib.pyplot as plt
from api.bybit.bybit import Bybit
from bot.get_iv import spot_ohlc

def term_structure(basecoin: str, plt_save_path: str):
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    op_tickers = (
        pd.DataFrame(bybit.send_request('GET',
                                        'public',
                                        target_path='/v5/market/tickers',
                                        params={'category':'option', 'baseCoin': basecoin})
                     .json().get('result').get('list'))
            .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
            .assign(CP = lambda df: df['symbol'].str.slice(-1))
            .reset_index(drop=True)
    )

    bid = op_tickers[['symbol', 'bid1Price', 'bid1Size', 'bid1Iv', 'indexPrice', 'K', 'CP']].assign(AskBid = 'Bid')
    ask = op_tickers[['symbol', 'ask1Price', 'ask1Size', 'ask1Iv', 'indexPrice', 'K', 'CP']].assign(AskBid = 'Ask')
    bid.columns = ['Symbol', 'Price', 'Size', 'Iv', 'IndexPrice', 'K', 'CP', 'AskBid']
    ask.columns = ['Symbol', 'Price', 'Size', 'Iv', 'IndexPrice', 'K', 'CP', 'AskBid']
    askbid = (
        pd.concat([ask, bid]).reset_index(drop=True)
            .assign(EXPIRY = lambda df: df['Symbol'].apply(lambda x: x.split('-')[1]))
            .assign(EXPIRY = lambda df: df['EXPIRY'].apply(lambda x: datetime.strptime(x, '%d%b%y')))
            .assign(T = lambda df: (df['EXPIRY'].apply(lambda x: x - datetime.now())).dt.days)
            .sort_values('EXPIRY')
    )
    askbid[['Price', 'Size', 'Iv', 'IndexPrice']] = askbid[['Price', 'Size', 'Iv', 'IndexPrice']].astype(float)

    S = spot_ohlc(limit='1')['last'].squeeze()
    K = round(S/500)*500

    sns.set_style('whitegrid')

    g = sns.FacetGrid(data=askbid.pipe(lambda df: df[(df['K']==K)&(df['T']<=40)]).sort_values('T'), col='CP')
    g.map_dataframe(sns.scatterplot, x='T', y='Iv', hue='AskBid', size='Size')
    g.map_dataframe(sns.lineplot, x='T', y='Iv', hue='AskBid')
    g.add_legend()
    g.set_axis_labels('T', f'''Iv for Stirke={K}''')
    plt.savefig(plt_save_path)