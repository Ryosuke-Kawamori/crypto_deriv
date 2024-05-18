from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import redis
import ordjson

templates = Jinja2Templates(directory='templates')
app = FastAPI()
app.mount(
    '/market_monitor',
    StaticFiles(
        directory='/'.join(
            os.path.abspath(__file__)
                .replace('\\', '/')
                .split('/')[:-1]
        )
    ),
    name='market_monitor',
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Tickers to watch
tickers = ['BTCUSDT']
@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse('main.html', {
        'request': request,
        'tickers': tickers,
    })

async def listen():
    ps = redis.Redis().pubsub()
    ps.subscribe('hoge')
    while True:
        for msg in ps.listen():
            yield orjson.loads(msg['data'])

@app.websocket('/ws')
async def stream_data(websocket: WebSocket):
    await websocket.accept()
    async for data in listen(channel='hoge'):
        if websocket.client_state.CONNECTED:
            await websocket.send_json(data)