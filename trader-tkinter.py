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

#%%

exchange = ccxt.kucoinfutures({
    'adjustForTimeDifference': True,
    **creds
})
# exchange.verbose = True

securities = pd.DataFrame(exchange.load_markets()).transpose()

##%%

def get_symbol(base, quote): return f'{base}/{quote}:{quote}'
def get_symbolId(base, quote): return securities.loc[get_symbol(base, quote)].id

def closePosition(symbolId, type = 'market'):
    position = getPosition(symbolId)

    opposite_side = 'sell' if position['currentQty'] > 0 else 'buy'
    cancel_params = {'reduceOnly': True, 'leverage': position['realLeverage']}
    cancel_order = exchange.createOrder(symbolId, type, opposite_side, position['currentQty'], price=position['avgEntryPrice'], params=cancel_params)
    exchange.futuresPrivateDeleteStopOrders(params={'symbol': symbolId})

def closeAllPositions():
    for symbolId in [x['symbol'] for x in exchange.futuresPrivateGetPositions(params={})['data']]: closePosition(symbolId=symbolId)

def getPosition(symbolId): 
    return [x for x in exchange.futuresPrivateGetPositions(params={'symbol': symbolId})['data']  if x['symbol'] == symbolId][0]

def openPosition(symbolId, direction=None, type = 'market'):
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

    stopLossPrice = (varShortSL.get() if direction == -1 else varLongSL.get())

    stop_range = (current_price - stopLossPrice)
    size = risk / stop_range  * direction

    type = 'market'
    side = 'buy' if direction == 1 else 'sell'
    stopLoss_type = 'market'
    # takeProfit_type = 'market'

    opposite_side = 'sell' if side == 'buy' else 'buy'
    stoploss_direction = 'down' if side == 'buy' else 'up'
    # takeProfit_direction = 'up' if side == 'buy' else 'down'


    price = current_price

    pprint(dict(symbolId=symbolId, type=type, price=price, stopLossPrice=stopLossPrice, size=size, stop_range=stop_range, leverage=leverage))
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
##%%


symConfigs = {}
symVars = {}

def loadSymbolConfig(symbolId):
    symConfigs[symbolId] = {}
    if os.path.exists('config.json'):
        with open('config.json') as f: 
            js = json.loads(f.read());
            if symbolId in js['symConfigs']:
                for k, v in js['symConfigs'][symbolId].items(): 
                    symConfigs[symbolId][k] = v

    for k, v in symConfigs[symbolId].items(): 
        symVars[k].set(v)

def saveSymbolConfig(symbolId):
    js = {'symConfigs': {symbolId:{}}}
    if os.path.exists('config.json'):
        with open('config.json') as f: 
            js = json.loads(f.read());
            if not symbolId in js['symConfigs']: js['symbols'] = {}
    js['symConfigs'][symbolId] = symConfigs[symbolId]

    with open('config.json', "w") as f: f.write(json.dumps(js))
    # for wdg in ['LEVERAGE', 'LONG_SL', 'SHORT_SL']:

def setSymConfig(symbolId, k, v):
    if not symbolId in symConfigs: symConfigs[symbolId] = {}
    symConfigs[symbolId][k] = v
    saveSymbolConfig(symbolId=symbolId)



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

##################################
### Top frame
# fromTop = Frame(root)
# fromTop.pack()
padding = {'padx': 5, 'pady': 5, 'sticky': tk.W}

def addLabeledVar(name, varType, initialValue, row, column, **kw):
    lbl_text = ttk.Label(master=root, text=f'{name}:')
    lbl_text.grid(column=column, row=row, columnspan=3, **kw['padding'])

    variable = varType(root, initialValue, name=name)
    lbl_var = Label(master=root)
    lbl_var.grid(column=column+4, row=row, columnspan=2, **kw['padding'])

    lbl_var.config(textvariable=variable)
    return variable
varRisk = addLabeledVar("risk", tk.DoubleVar, 20, 0, 0, padding=padding)
varLeverage = addLabeledVar("leverage", tk.DoubleVar, 10, 0, 10, padding=padding)
varOrderType = addLabeledVar("OrderType", tk.DoubleVar, 'market', 0, 20, padding=padding)
varSymbol = addLabeledVar("symbol", tk.StringVar, 'ETHUSDTM', 1, 0, padding=padding)
varLongSL = addLabeledVar("LongSL", tk.DoubleVar, None, 1, 10, padding=padding)
varShortSL = addLabeledVar("ShortSL", tk.DoubleVar, 2085, 1, 20, padding=padding)

symVars = {'LONG_SL': varLongSL, 'SHORT_SL': varShortSL, 'LEVERAGE': varLeverage}
allVars = {**symVars, 'ORDER_TYPE': varOrderType, 'SYMBOL': varSymbol}

symbolId = 'ETHUSDTM'
loadSymbolConfig(symbolId)

# def bindChangeVar(key, variable, askFunc):
#     def chgVar(event):
#         newValue = askFunc(f'Change {variable._name}', 'New value:', initialvalue=variable.get())
#         if newValue != None:
#             variable.set(newValue)
#             saveSymbolConfig(symbolId)
    
#     root.bind(key, chgVar)

# bindChangeVar('<Control-S>', varSymbol, askstring)
# bindChangeVar('<Control-R>', varRisk, askfloat)
# bindChangeVar('<Control-L>', varLeverage, askfloat)
# bindChangeVar('<Alt-l>', varLongSL, askfloat)
# bindChangeVar('<Alt-s>', varShortSL, askfloat)


def makeChangeVar(varName, askFunc):
    def chgVar(event):
        global symbolId
        variable = allVars[varName]
        newValue = askFunc(f'Change {variable._name}', 'New value:', initialvalue=variable.get())
        if newValue != None:
            variable.set(newValue)
            if variable == varSymbol:
                symbolId = newValue
                loadSymbolConfig(symbolId)
            elif variable in [varLeverage, varLongSL, varShortSL]:
                setSymConfig(symbolId, varName, newValue)
    return chgVar

# root.bind(key, chgVar)

root.bind('<Control-S>', makeChangeVar('SYMBOL', askstring))
root.bind('<Control-R>', makeChangeVar('RISK', askfloat))
root.bind('<Control-L>', makeChangeVar('LEVERAGE', askfloat))
root.bind('<Alt-l>', makeChangeVar('LONG_SL', askfloat))
root.bind('<Alt-s>', makeChangeVar('SHORT_SL', askfloat))


##################################


# frmPositions = Frame(root)
# frmPositions.pack()

# treePositions = ttk.Treeview(frmPositions)

# positions = exchange.futuresprivate_get_positions()['data']
# treePositions.set_children
##################################

def evOpenPosition(event):
    if not varSymbol.get():
        showerror(title="Symbol missing", message="Please select symbol")
        return
    
    direction = 1 - 2 * (event.keysym == 'S')
    shortOrLong = 'Short' if direction == -1 else 'Long'
    # sl = askfloat("Stoploss", "Please enter stoploss price")
    # print(sl)

    if askokcancel(title=f'Opening {shortOrLong} position', message="Go ahead ?"):
        openPosition(varSymbol.get(), direction=direction)
    else:
        return


root.bind('<L>', evOpenPosition)
root.bind('<S>', evOpenPosition)


def evClosePosition(event):
    if not varSymbol.get():
        showerror(title="Symbol missing", message="Please select symbol")
        return
    
    if askokcancel(title=f'Closing position', message="Go ahead ?"):
        closePosition(symbolId=varSymbol.get())
    else:
        return

root.bind('<C>', evClosePosition)

root.mainloop() 

#%%

# positions = exchange.futuresprivate_get_positions()['data']

# positions
#%%