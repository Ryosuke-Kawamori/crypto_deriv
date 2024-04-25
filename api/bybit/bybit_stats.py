import os
import pandas as pd
from api.bybit.bybit import Bybit
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def trade_pnl(fig_path: str):
    bybit = Bybit(os.getenv('BYBIT_APIKEY'), os.getenv('BYBIT_SECRET'))
    response = bybit.send_request('GET', 'private', target_path='/v5/execution/list', params={'category':'option', 'limit': '50'})
    trades = pd.DataFrame(response.json().get('result').get('list'))

    delivery_price_list = []
    for _symbol in trades['symbol'].drop_duplicates().tolist():
        response = bybit.send_request('GET', 'public', '/v5/market/delivery-price',
                                      params = {'category': 'option', 'symbol': _symbol})
        delivery_price_list.append(pd.DataFrame(response.json().get('result').get('list')))
    delivery_price = pd.concat(delivery_price_list)

    pnl = (
        pd.merge(trades, delivery_price)
        [['symbol', 'markPrice', 'execPrice', 'markIv', 'orderQty', 'side', 'seq', 'indexPrice', 'execFee', 'execQty', 'deliveryPrice', 'execTime', 'deliveryTime']]
            .assign(K = lambda df: df['symbol'].apply(lambda x: x.split('-')[2]).astype(int))
            .assign(CP = lambda df: df['symbol'].apply(lambda x: x.split('-')[3]))
    )
    pnl[['markPrice', 'execPrice', 'markIv', 'orderQty', 'indexPrice', 'execFee', 'execQty', 'deliveryPrice']] = \
        pnl[['markPrice', 'execPrice', 'markIv', 'orderQty', 'indexPrice', 'execFee', 'execQty', 'deliveryPrice']].astype(float)

    pnl[['execTime', 'deliveryTime']] = pnl[['execTime', 'deliveryTime']].apply(lambda x: x.str.slice(0,10).astype(int)).applymap(lambda x: datetime.fromtimestamp(x))

    pnl = (
        pnl
            .assign(KnockIn = lambda df: ((df['CP']=='P') & (df['K']>=df['deliveryPrice'])) | ((df['CP']=='C') & (df['K']<=df['deliveryPrice'])))
            .assign(PnL = lambda df: (df['execPrice']*df['orderQty']))
            .assign(PnL = lambda df: df['PnL'].mask(df['KnockIn'], (df['K']-df['indexPrice'])*(df['CP'].replace({'C':1, 'P': -1}))*(df['side'].replace({'Sell': 1, 'Buy': -1}))))
            .assign(PnL = lambda df: df['PnL']-df['execFee'])
    )

    daily_pnl = (
        pnl.groupby(['deliveryTime'])[['execQty', 'PnL']].sum()
            .assign(CumulativePnL = lambda df: df['PnL'].cumsum())
            .reset_index()
    )

    sns.set_style('whitegrid')
    fig, axes = plt.subplots(figsize=(10,4), nrows=2, sharex=True)
    ax=axes[0]
    sns.lineplot(data=daily_pnl, x='deliveryTime', y='CumulativePnL', marker='o', ax=ax)
    ax.set_ylabel('Cumulative PnL($)')

    ax=axes[1]
    ax.bar(daily_pnl['deliveryTime'], daily_pnl['execQty'])
    ax.set_ylabel('Qty')
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.savefig(fig_path, bbox_inches='tight')
    return pnl

