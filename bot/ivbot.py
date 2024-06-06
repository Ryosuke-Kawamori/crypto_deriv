import discord
import os
from discord.ext import commands
from bot.gamma_exposure import gamma_exposure
from bot.get_iv import last_iv, askbid_iv
from api.bybit.bybit_stats import pnl as bybitpnl
from bot.term_structure import term_structure

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.getenv('TOKEN')

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('Login')

@bot.command()
async def neko(ctx):
    await ctx.send('にゃーん')

# Implied Vilatility
@bot.command()
async def iv(ctx, basecoin: str = 'BTC', n_day: str = '0'):
    last_iv(basecoin=basecoin, n_day=int(n_day))
    askbid_iv(basecoin=basecoin, n_day=int(n_day))
    await ctx.send(file=discord.File('askbidiv.png'))
    await ctx.send(file=discord.File('iv.png'))
    await ctx.send(file=discord.File('table.png'))

# PnL Plot
@bot.command()
async def pnl(ctx):
    bybitpnl('daily_pnl.png')
    await ctx.send(file=discord.File('daily_pnl.png'))

# Gamma Exposure
@bot.command()
async def gexp(ctx, basecoin: str = 'BTC', gamma_type: str = 'general'):
    gamma_exposure(basecoin = basecoin, gamma_type=gamma_type,  plt_save_path = 'gamma_exposure.png')
    await ctx.send(file=discord.File('gamma_exposure.png'))

# Term Structure
@bot.command()
async def terms(ctx, basecoin: str = 'BTC'):
    term_structure(basecoin = basecoin, plt_save_path = 'termstructure.png')
    await ctx.send(file=discord.File('termstructure.png'))

# Show Orders
@bot.command()
async def orders(ctx):
    await ctx.send(file=discord.File('orders.png'))

@bot.command()
async def ping(ctx):
    await ctx.reply("Pong!")

@bot.command()
async def echo(ctx: commands.Context, arg: str):
    await ctx.send(arg)

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)