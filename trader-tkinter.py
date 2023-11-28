#%%
import tkinter as tk
# from tkinter import *
from tkinter import ttk
import tkinter.font
# from tkinter import Tk, font, Frame
from tkinter import Frame
from tkinter.simpledialog import *
from tkinter.messagebox import *
from tkinter.ttk import Button, Label 
  
import pandas as pd
import ccxt

from pprint import pprint
##%%
from api_config import *
import os
import json
from collections import defaultdict

#%%

exchange = ccxt.kucoinfutures({
    'adjustForTimeDifference': True,
    **creds
})
# exchange.verbose = True

securities = pd.DataFrame(exchange.load_markets()).transpose()

##%%

symbolId = None
position = None
sl_order = tp_order = None
position_exit_order = None

# def get_symbol(base, quote): return f'{base}/{quote}:{quote}'
# def get_symbolId(base, quote): return securities.loc[get_symbol(base, quote)].id

# def closePosition(symbolId, type = 'market'):
#     global position_exit_order
#     position = getPosition(symbolId)

#     opposite_side = 'sell' if position['currentQty'] > 0 else 'buy'
#     cancel_params = {'reduceOnly': True, 'leverage': position['realLeverage']}
#     position_exit_order = exchange.createOrder(symbolId, type, opposite_side, position['currentQty'], price=position['avgEntryPrice'], params=cancel_params)
#     exchange.futuresPrivateDeleteStopOrders(params={'symbol': symbolId})

# def closeAllPositions():
#     for symbolId in [x['symbol'] for x in exchange.futuresPrivateGetPositions(params={})['data']]: closePosition(symbolId=symbolId)

# def getPosition(symbolId): 
#     return [x for x in exchange.futuresPrivateGetPositions(params={'symbol': symbolId})['data']  if x['symbol'] == symbolId][0]


# securities
##%%



#%%
#%%
root = tk.Tk()
root.geometry("1200x300") 

# root.option_add('*Font', '24')
def_font = tk.font.nametofont("TkDefaultFont")
def_font.config(family='Arial',size=18, weight='bold')
root.option_add("*Font", def_font)

def quit(event):
    root.quit()

root.bind('<Control-Q>', quit) 

################################
##  Variables

padding = {'padx': 5, 'pady': 5, 'sticky': tk.W}

def addLabeledVar(name, varType, initialValue, row, column, **kw):
    lbl_text = ttk.Label(master=root, text=f'{name}:')
    lbl_text.grid(column=column, row=row, columnspan=3, **kw['padding'])

    variable = varType(root, initialValue, name=name)
    lbl_var = Label(master=root)
    lbl_var.grid(column=column+4, row=row, columnspan=2, **kw['padding'])

    lbl_var.config(textvariable=variable)
    return variable
varRisk = addLabeledVar("Risk", tk.DoubleVar, 20, 0, 0, padding=padding)
varLeverage = addLabeledVar("Leverage", tk.DoubleVar, None, 0, 10, padding=padding)
varOrderType = addLabeledVar("OrderType", tk.StringVar, 'market', 0, 20, padding=padding)
varSymbol = addLabeledVar("Symbol", tk.StringVar, None, 1, 0, padding=padding)
varLongSL = addLabeledVar("LongSL", tk.DoubleVar, None, 1, 10, padding=padding)
varShortSL = addLabeledVar("ShortSL", tk.DoubleVar, None, 1, 20, padding=padding)


# def openPosition(direction=None, type = 'market'):
#     if not symbolId:
#         showerror('Please select symbol')
#         return
    
#     ticker = exchange.fetchTicker(symbolId)
#     current_price = ticker['last']
#     risk = 100.0
#     ###
#     # balance = exchange.fetchBalance (params = {})
#     # free_balance = balance['free'][quote]
#     # free_balance
#     ###
#     leverage = varLeverage.get()
#     # direction = -1
#     # 
#     # marg = 0.005
#     # stopLossPrice = current_price * (1 - direction * marg)
#     # takeProfitPrice = current_price * (1 + direction * 2*marg)
#     # stopLossPrice = 60.03
#     # takeProfitPrice = 51.72

#     stopLossPrice = (varShortSL.get() if direction == -1 else varLongSL.get())

#     stop_range = (current_price - stopLossPrice)
#     size = risk / stop_range  * direction

#     type = 'market'
#     side = 'buy' if direction == 1 else 'sell'
#     stopLoss_type = 'market'
#     # takeProfit_type = 'market'

#     opposite_side = 'sell' if side == 'buy' else 'buy'
#     stoploss_direction = 'down' if side == 'buy' else 'up'
#     # takeProfit_direction = 'up' if side == 'buy' else 'down'


#     price = current_price

#     pprint(dict(symbolId=symbolId, type=type, price=price, stopLossPrice=stopLossPrice, size=size, stop_range=stop_range, leverage=leverage))
#     params = {
#         'leverage': leverage,
#     }
#     order = exchange.createOrder(symbolId, type, side, size, price=price, params=params)


#     stopLoss_params = {
#         'leverage': leverage,
#         'stopLossPrice': stopLossPrice,
#         # 'stopPriceType':'MP',
#         'stop': stoploss_direction,
#         'reduceOnly': False
#     }
#     stopLoss_order = exchange.createOrder(symbolId, stopLoss_type, opposite_side, size, price=price, params=stopLoss_params)

#     # takeProffit_params = {
#     #     'leverage': leverage,
#     #     'takeProfitPrice': takeProfitPrice,
#     #     # 'takeProfitPriceType':'MP',
#     #     'stop': takeProfit_direction,
#     #     'reduceOnly': False
#     # }
#     # takeProffit_order = exchange.createOrder(symbolId, takeProfit_type, opposite_side, size, price=price, params=takeProffit_params)

#     xposition = dict(order=order, stopLoss_order=stopLoss_order, 
#                     #  takeProffit_order=takeProffit_order
#                      )
#     return xposition
##################################


#%% 
#####
def loadSymConfig():
    if not os.path.exists('config.json'):
        with open('config.json', "w") as f: f.write(json.dumps({'symConfigs': {}}));
    # print(symbolId)
    # global varLongSL, varShortSL, varLeverage
    varSymbol.set(symbolId)
    varLongSL.set(None); varShortSL.set(None); #varLeverage.set(None);

    if os.path.exists('config.json'):
        with open('config.json') as f: 
            js = json.loads(f.read())
            if symbolId in js['symConfigs']: 
                #  js['symConfigs'][symbolId] = defaultdict(lambda: None)
                # print('aaa->', js['symConfigs'][symbolId])
                if 'LONG_SL' in js['symConfigs'][symbolId]: varLongSL.set(js['symConfigs'][symbolId]['LONG_SL'])
                if 'SHORT_SL' in js['symConfigs'][symbolId]: varShortSL.set(js['symConfigs'][symbolId]['SHORT_SL'])
                if 'LEVERAGE' in js['symConfigs'][symbolId]: varLeverage.set(js['symConfigs'][symbolId]['LEVERAGE'])

def evChangeSymbol(ev):
    global symbolId
    newValue = askstring('Change symbol', 'Enter Symbol:')
    if newValue:
        symbolId = newValue        
        loadSymConfig()

root.bind('<s> <c>', evChangeSymbol)

symbolId = 'ETHUSDTM'
loadSymConfig()
#####

def saveSymbolConfig(fldName, value):
    if not os.path.exists('config.json'):
        with open('config.json', "w") as f: f.write(json.dumps({'symConfigs': {}}));
    js = None
    with open('config.json') as f: js = json.loads(f.read())

    if not 'symConfigs' in js: js['symConfigs'] = {}
    if not symbolId in js['symConfigs']: js['symConfigs'][symbolId] = {}
    js['symConfigs'][symbolId][fldName] = value

    with open('config.json', "w") as f: f.write(json.dumps(js))


def evChangeShortSL(ev):
        newValue = askfloat(f'Change SHORT_SL', 'New value:')
        if newValue != None:
            varShortSL.set(newValue)    
            saveSymbolConfig('SHORT_SL', newValue)


def evChangeLongSL(ev):
        newValue = askfloat(f'Change LONG_SL', 'New value:')
        if newValue != None:
            varLongSL.set(newValue)
            saveSymbolConfig('LONG_SL', newValue)

def evChangeLeverage(ev):
        newValue = askfloat(f'Change Leverage', 'New value:')
        if newValue != None:
            varLeverage.set(newValue)
            saveSymbolConfig('LEVERAGE', newValue)



root.bind('<l><s><l>', evChangeLongSL)
root.bind('<s><s><l>', evChangeShortSL)
root.bind('<l><v><r>', evChangeLeverage)
# frmPositions = Frame(root)
# frmPositions.pack()

# treePositions = ttk.Treeview(frmPositions)

# positions = exchange.futuresprivate_get_positions()['data']
# treePositions.set_children
##################################

# def evOpenPosition(event):
#     if not varSymbol.get():
#         showerror(title="Symbol missing", message="Please select symbol")
#         return
    
#     direction = 1 - 2 * (event.keysym == 'S')
#     shortOrLong = 'Short' if direction == -1 else 'Long'
#     # sl = askfloat("Stoploss", "Please enter stoploss price")
#     # print(sl)

#     if askokcancel(title=f'Opening {shortOrLong} position', message="Go ahead ?"):
#         openPosition(varSymbol.get(), direction=direction)
#     else:
#         return


# root.bind('<L>', evOpenPosition)
# root.bind('<S>', evOpenPosition)


# def evClosePosition(event):
#     if not varSymbol.get():
#         showerror(title="Symbol missing", message="Please select symbol")
#         return
    
#     if askokcancel(title=f'Closing position', message="Go ahead ?"):
#         closePosition(symbolId=varSymbol.get())
#     else:
#         return

# root.bind('<C>', evClosePosition)


root.mainloop() 

#%%

# positions = exchange.futuresprivate_get_positions()['data']

# positions
#%%