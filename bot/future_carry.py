import matplotlib.pyplot as plt
from datetime import datetime, date
import seaborn as sns
import os
import pandas as pd

from api.bybit.bybit import Bybit

pd.set_option('display.max.columns', 30)

def future_carry(plt_save_path: str = 'future_carry.png')
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    futures = (
        pd.DataFrame(bybit.send_request('GET',
                                        'public',
                                        target_path='/v5/market/tickers',
                                        params={'category':'linear'})
                     .json().get('result').get('list'))
        .pipe(lambda df: df[df['symbol'].str.match('BTC-[0-9]{2}[A-Z]{3}[0-9]{2}')])
        .assign(deliveryTime = lambda df: df['deliveryTime'].str.slice(0,10).apply(lambda x: datetime.fromtimestamp(int(x))))
        .assign(N = lambda df: df['deliveryTime'].dt.date.apply(lambda x: x - date.today()).dt.days)
        .reset_index(drop=True)
        )

    cols_float = list(set(futures.columns) - set(['symbol', 'deliveryTime', 'N', 'fundingRate']))
    futures[cols_float] = futures[cols_float].apply(lambda x: x.replace('', 0)).astype(float)
    futures = futures.assign(CarryYearly = lambda df: df['basis']/df['indexPrice']*365/df['N']*100)

    sns.set_style('whitegrid')
    fig, ax = plt.subplots(figsize=(6, 4))

    axtwin = ax.twinx()
    axtwin.bar(futures['deliveryTime'], futures['openInterest'], width=5, color='gray')

    sns.lineplot(data=futures, x='deliveryTime', y='CarryYearly', marker='o', ax=ax)
    ax.tick_params(axis='x', labelrotation=90)
    ax.set_xlabel('EXPIRY')
    ax.set_ylabel('Carry(%, Yearly)')
    plt.savefig(plt_save_path, bbox_inches='tight')