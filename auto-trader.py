
#%%


import uuid
import pandas as pd
import sys
from pprint import pprint


import sys, os
sys.path.append(os.path.abspath('.'))

from itertools import *
import ccxt

import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
from threading import Thread

from api_config import *

import multiprocessing

#%%

#%%

# stop_trades_thread = False

async def ws_trades():
    exchange = ccxtpro.kucoinfutures({'newUpdates': False})
    while True:
        trades = await exchange.watch_trades("ALGOUSDTM")
        print(exchange.iso8601(exchange.milliseconds()), trades)
        # if stop(): break
    await exchange.close()

# orders_thread = Thread(target=ws_trades, args=(lambda: stop_trades_thread,))

proc = multiprocessing.Process(target=ws_trades, args=())
proc.start()
# Terminate the process
# proc.terminate()  # sends a SIGTERM

# orders_loop = asyncio.new_event_loop()

# def setup_loop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_forever()

# orders_thread = Thread(target=setup_loop, args=(orders_loop,))
# orders_thread.start()
# orders_future = asyncio.run_coroutine_threadsafe(ws_orders(lambda: stop_orders_thread), orders_loop)  

#%%

#%%

