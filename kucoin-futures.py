#%%
import ccxt
import pandas as pd
import sys
from pprint import pprint

#%%
print('python', sys.version)
print('CCXT Version:', ccxt.__version__)

#%%

exchange = ccxt.kucoinfutures({
    'adjustForTimeDifference': True,
    # "apiName": 'ku-futures',
    "apiKey": '655f763effa2720001d2f3f4',
    "secret": '1f52656e-dd97-4c72-9a8b-eb0dc3171f8d',
    'password': '#2M%RSN$c*4f1jDYVCiOUmTJf$#RYF',
})
# exchange.verbose = True

# securities = pd.DataFrame(exchange.load_markets()).transpose()
# pprint(securities)
securities
#%%
pprint(exchange.fetch_balance())
#%%
# exchange.fetch_balance()
# exchange.fetch_my_trades()
#%%

price = 0.36
size = 10
stopPrice = 0.35
leverage = 10

params = {"leverage": leverage, 
          "stop-loss": {"side":"sell", "stop":"down", "stopPriceType":"TP", "stopPrice": stopPrice}
}

# take-profit:side=sell, stop=up, stopPriceType and stopPrice are set according to your needs}

order = exchange.createOrder('ADA/USDT:USDT', 'market', 'buy', 10, price=price, params=params)
pprint(order)

#%%

#%%
# canceled_orders = exchange.cancel_order(order['id'])
canceled_orders = exchange.cancel_all_orders()
canceled_orders

#%%

# exchange.fetch_open_orders()
# exchange.fetch_closed_orders()
exchange.fetch_positions()

#%%

#%%
