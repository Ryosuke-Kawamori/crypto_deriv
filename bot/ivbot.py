import discord
import os
from bot.get_iv import get_last_iv, get_askbid_iv
from api.bybit.bybit_stats import trade_pnl

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
        get_last_iv()
        get_askbid_iv()
        #await message.channel.send(file=discord.File('price.png'))
        await message.channel.send(file=discord.File('askbidiv.png'))
        await message.channel.send(file=discord.File('iv.png'))
        await message.channel.send(file=discord.File('table.png'))
    # PnL
    if message.content == '/pnl':
        trade_pnl('./daily_pnl.png')
        await message.channel.send(file=discord.File('./daily_pnl.png'))


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)