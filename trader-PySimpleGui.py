#%%
import PySimpleGUI as sg 
  
import pandas as pd
import ccxt

from pprint import pprint
import os
import json
## %%
from api_config import *

##

exchange = ccxt.kucoinfutures({
    'adjustForTimeDifference': True,
    **creds
})
# exchange.verbose = True

securities = pd.DataFrame(exchange.load_markets()).transpose()

## 

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
    leverage = symConfigs[symbolId]['LEVERAGE']
    # direction = -1
    # 
    # marg = 0.005
    # stopLossPrice = current_price * (1 - direction * marg)
    # takeProfitPrice = current_price * (1 + direction * 2*marg)
    # stopLossPrice = 60.03
    # takeProfitPrice = 51.72

    stopLossPrice = (symConfigs[symbolId]['SHORT_SL'] if direction == -1 else symConfigs[symbolId]['LONG_SL'])

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


import PySimpleGUI as sg

sg.theme('BluePurple')

layout = [
    [sg.Text('Risk:'), sg.Text(key='-OUTPUT-RISK-', size=(10,1)), sg.Text('Leverage:'), sg.Text(key='-OUTPUT-LEVERAGE-', size=(10,1))],
    [sg.Text('Symbol:'), sg.Text(key='-OUTPUT-SYMBOL-', size=(10,1)), sg.Text('Long SL:'), sg.Text(key='-OUTPUT-LONG_SL-', size=(10,1)), sg.Text('Short SL:'), sg.Text(key='-OUTPUT-SHORT_SL-', size=(10,1))],
]

fields = dict(
    SYMBOL=dict(type=str),
    RISK=dict(type=float),
    LEVERAGE=dict(type=float),
    LONG_SL=dict(type=float),
    SHORT_SL=dict(type=float),
)
sg.set_options(font=("Arial", 24))
window = sg.Window('PKey Trader', layout, finalize=True, element_justification='r')
window.bind('<Control-S>', 'INPUT:SYMBOL' )
window.bind('<Control-R>', 'INPUT:RISK' )
window.bind('<Control-L>', 'INPUT:LEVERAGE' )
window.bind('<Alt-L>', 'INPUT:LONG_SL' )
window.bind('<Alt-S>', 'INPUT:SHORT_SL' )
window.bind('<L>', 'POSITION:LONG' )
window.bind('<C>', 'POSITION:SHORT' )

window.bind('<Control-Q>', 'Exit' )
# '-INPUT-RISK'

symConfigs = {}

def loadSymbolConfig(symbolId):
    window[f'-OUTPUT-SYMBOL-'].update(symbolId)
    symConfigs[symbolId] = {}
    if os.path.exists('config.json'):
        with open('config.json') as f: 
            js = json.loads(f.read());
            if symbolId in js['symConfigs']:
                for k, v in js['symConfigs'][symbolId].items(): 
                    symConfigs[symbolId][k] = v

    for k, v in symConfigs[symbolId].items(): 
        window[f'-OUTPUT-{k}-'].update(v)

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

symbolId = 'ETHUSDTM'
loadSymbolConfig(symbolId)

while True:  # Event Loop
    event, values = window.read()
    # if event is None:
    #     continue

    print(event, values)

    if event:
        if event.startswith('INPUT'):
            fldName = event.split(':')[1]
            field = fields[fldName]
            print('field:', fldName, field)
            # inp = sg.popup_get_text(f'Enter {fldName}' )
            # window[f'-OUTPUT-{fldName}-'].update(inp)
            evPopup, valPopup = sg.Window(fldName,
                    [[sg.T(f'Enter {fldName}'), sg.In(key='-VAL-')],
                    [sg.OK(), sg.Exit() ]]).read(close=True)
            print('Popup:',evPopup, valPopup['-VAL-'])
            if evPopup == 'OK' and valPopup:
                val = fields[fldName]['type'](valPopup['-VAL-'])
                print('Popup:',evPopup, valPopup['-VAL-'], val)
                window[f'-OUTPUT-{fldName}-'].update(val)
                if fldName == 'SYMBOL':
                    symbolId = val
                    loadSymbolConfig(symbolId)
                elif fldName in ['LEVERAGE', 'LONG_SL', 'SHORT_SL']:
                    setSymConfig(symbolId, fldName, val)
        elif event.startswith('POSITION'):
            
            action = event.split(':')[1]
            if action in ['LONG', 'SHORT']:
                # if sg.popup_ok_cancel(f'Confirm {action}') == 'OK':
                wnd = sg.Window(title=f'{action}', layout=[[sg.T(f'Please confirm {action}')], [sg.Ok(), sg.Exit()]], finalize=True, modal=True, return_keyboard_events=False, auto_close=True)
                wnd.bind('<Esc>', 'Exit')
                wnd.bind('<Enter>', 'OK')
                ev, vals = wnd.read(close=True, timeout_key='<Esc>')
                print(ev,vals)
            # pass
                # if ev == 'OK':
                #     direction = 1 - 2 * (action == 'SHORT')
                #     openPosition(symbolId, direction)
        # sg.popup
        
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()

#%%
