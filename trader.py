#%%
import tkinter as tk
from tkinter import ttk 

from tkinter import Tk, font
from tkinter.simpledialog import *
from tkinter.messagebox import *
from tkinter.ttk import Button, Label 
  
import pandas as pd
import ccxt

from pprint import pprint
#%%
from api_config import *

#%%

exchange = ccxt.kucoinfutures({
    'adjustForTimeDifference': True,
    **creds
})
# exchange.verbose = True

securities = pd.DataFrame(exchange.load_markets()).transpose()

#%%

def get_symbol(base, quote): return f'{base}/{quote}:{quote}'
def get_symbolId(base, quote): return securities.loc[get_symbol(base, quote)].id

def close_position(symbolId, type = 'market'):
    position = get_position(symbolId)

    opposite_side = 'sell' if position['currentQty'] > 0 else 'buy'
    cancel_params = {'reduceOnly': True, 'leverage': position['realLeverage']}
    cancel_order = exchange.createOrder(symbolId, type, opposite_side, position['currentQty'], price=position['avgEntryPrice'], params=cancel_params)
    exchange.futuresPrivateDeleteStopOrders(params={'symbol': symbolId})

def close_all_positions():
    for symbolId in [x['symbol'] for x in exchange.futuresPrivateGetPositions(params={})['data']]: close_position(symbolId=symbolId)

def get_position(symbolId): 
    return [x for x in exchange.futuresPrivateGetPositions(params={'symbol': symbolId})['data']  if x['symbol'] == symbolId][0]

def openPosition(symbolId, direction=None, stopLossPrice=None, type = 'market'):
    ticker = exchange.fetchTicker(symbolId)
    current_price = ticker['last']
    risk = 100.0
    ###
    # balance = exchange.fetchBalance (params = {})
    # free_balance = balance['free'][quote]
    # free_balance
    ###
    leverage = varLeverage.get()
    # direction = -1
    # 
    # marg = 0.005
    # stopLossPrice = current_price * (1 - direction * marg)
    # takeProfitPrice = current_price * (1 + direction * 2*marg)
    # stopLossPrice = 60.03
    # takeProfitPrice = 51.72

    stop_range = (current_price - stopLossPrice)
    size = risk / stop_range  * direction

    type = 'market'
    side = 'buy' if direction == 1 else 'sell'
    stopLoss_type = 'market'
    takeProfit_type = 'market'

    opposite_side = 'sell' if side == 'buy' else 'buy'
    stoploss_direction = 'down' if side == 'buy' else 'up'
    takeProfit_direction = 'up' if side == 'buy' else 'down'


    price = current_price


    params = {
        'leverage': leverage,
    }
    order = exchange.createOrder(symbolId, type, side, size, price=price, params=params)


    stopLoss_params = {
        'leverage': leverage,
        'stopLossPrice': stopLossPrice,
        # 'stopPriceType':'MP',
        'stop': stoploss_direction,
        'reduceOnly': False
    }
    stopLoss_order = exchange.createOrder(symbolId, stopLoss_type, opposite_side, size, price=price, params=stopLoss_params)

    # takeProffit_params = {
    #     'leverage': leverage,
    #     'takeProfitPrice': takeProfitPrice,
    #     # 'takeProfitPriceType':'MP',
    #     'stop': takeProfit_direction,
    #     'reduceOnly': False
    # }
    # takeProffit_order = exchange.createOrder(symbolId, takeProfit_type, opposite_side, size, price=price, params=takeProffit_params)

    xposition = dict(order=order, stopLoss_order=stopLoss_order, 
                    #  takeProffit_order=takeProffit_order
                     )
    return xposition
# securities
#%%
root = tk.Tk()
root.geometry("800x600") 

# root.option_add('*Font', '24')
def_font = tk.font.nametofont("TkDefaultFont")
def_font.config(family='Helvetica',size=18, weight='bold')
root.option_add("*Font", def_font)

padding = {'padx': 5, 'pady': 5, 'sticky': tk.W}
# risk labels
lbl_risk_lbl = ttk.Label(text="Risk per position:")
lbl_risk_lbl.grid(column=0, row=0, columnspan=3, **padding)

varRisk = tk.IntVar(root, 20, name='risk')
lbl_risk = Label()

lbl_risk.config(textvariable=varRisk)
lbl_risk.grid(column=4, row=0, columnspan=3, **padding)

# symbol labels
lbl_symbol_lbl = ttk.Label(text="Symbol:")
lbl_symbol_lbl.grid(column=0, row=1, columnspan=3, **padding)

varSymbol = tk.StringVar(master=root, value=None, name='Symbol')
lbl_symbol = Label()

lbl_symbol.config(textvariable=varSymbol)
lbl_symbol.grid(column=4, row=1, columnspan=3, **padding)


# symbol labels
lbl_leverage_lbl = ttk.Label(text="Leverage:")
lbl_leverage_lbl.grid(column=0, row=2, columnspan=3, **padding)

varLeverage = tk.IntVar(master=root, value=10, name='Leverage')
lbl_leverage = Label()

lbl_leverage.config(textvariable=varLeverage)
lbl_leverage.grid(column=4, row=2, columnspan=3, **padding)

def quit(event):
    root.quit()

root.bind('<Control-q>', quit) 



def chgSymbol(event):
    sym = askstring("Change symbol", "Symbol", initialvalue=varSymbol.get())
    if sym != None:
        print(sym)
        varSymbol.set(sym.upper())

root.bind('<Control-s>', chgSymbol)

def chgRisk(event):
    v = askinteger("Change risk per position", "Amount in USD", initialvalue=varRisk.get())
    if v != None:
        print(v)
        varRisk.set(v)

root.bind('<Control-r>', chgRisk)

def chgLeverage(event):
    v = askinteger("Change leverage", "New leverage", initialvalue=varLeverage.get())
    if v != None:
        print(v)
        varLeverage.set(v)

root.bind('<Control-l>', chgLeverage)


def evOpenPosition(event):
    if not varSymbol.get():
        showerror(title="Symbol missing", message="Please select symbol")
        return
    
    direction = 1 - 2 * (event.keysym == 's')

    sl = askfloat("Stoploss", "Please enter stoploss price")
    print(sl)

    if askokcancel(title=f'Opening {direction} position', message="Go ahead ?"):
        openPosition(varSymbol.get(), direction=direction,stopLossPrice=sl)
    else:
        return


root.bind('<Alt-l>', evOpenPosition)
root.bind('<Alt-s>', evOpenPosition)


def evClosePosition(event):
    if not varSymbol.get():
        showerror(title="Symbol missing", message="Please select symbol")
        return
    
    if askokcancel(title=f'Closing position', message="Go ahead ?"):
        close_position(symbolId=varSymbol.get())
    else:
        return

root.bind('<Alt-c>', evClosePosition)

root.mainloop() 

#%%