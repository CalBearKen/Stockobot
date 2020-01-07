from IPython.display import clear_output
from datetime import datetime
from statistics import mean
from matplotlib import pyplot as plt
import pandas as pd
import robin_stocks as robin
import threading
import logging
import getpass
import csv


"""Stockobot v0.1, doesn't do much yet
only outputs graph of stocks on watchlist"""

def initial_setup():
    """Generate Debug Log"""
    LOG_FILENAME = 'script.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.debug(now + " +Script started+")

    """Generate CSV Trading Tracker"""
    start_time = now
    with open('TradeLog.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        datapoints = ['start_time', 'trade_time', 'symbol', 'price', 'sell/buy']
        writer.writerow(datapoints)
    '''
    with open('watchlist.csv', 'w') as watchlist: #generates csv file for storing symbols to watch
        writer = csv.writer(watchlist, delimiter=',', quotechar='|')
        datapoints = ['symbol', 'time', 'price0', 'buy_price', 'sell_price', 'buy_date', 'sell_date']
        writer.writerow(datapoints)
    '''
    #script requires log in everytime and wipes the credential variables once token is received to increase security
    username = input("enter username:")
    password = getpass.getpass("enter password:")
    token_dict = robin.login(username, password)
    token = token_dict['access_token']
    username, password = 0, 0
    if token_dict != None:
        logging.debug(now + ' +Token received+')
    else:
        logging.warning(now + ' -Token NOT received!-')
    clear_output()
    print('Logged in successfully')

"""Strat: buy when current ticker is lowest of 1 week worth of tickers"""
def min_check(symbol, span='week'):
#check if current price is min of one week tickers
    price_list = tick_list(symbol, span)
    current_price = float(price_list.iloc[[-1]][1])
    minimum = min(price_list)
    prices = price_list[1]

    print('current price for '+str(symbol)+': '+str(current_price))
    if minimum == current_price:
        print('Current price for '+symbol+' is at one-week low, buy now')
    else:
        #price_list
        #frequency = len(price_list[price_list[1]==current_price])
        print('Current price for '+symbol+' is NOT at one-week low, wait')

def check_portfol():
    current_portfolio = robin.account.build_holdings()
    fundamental_info = robin.stocks.get_fundamentals('QCOM')
    fundamentals = {}
    hist_price = {}
    for key, info in current_portfolio.items():
        hist_price[key] = robin.stocks.get_historicals(key, span='week', bounds='regular')
        if float(current_portfolio[key]['percent_change']) > 25:
            print("fuck yea " + key)
        elif float(current_portfolio[key]['percent_change']) < -25: #stoploss
            print("Sell " + key + " now!")
        else: continue

"""Return a list of price changes between each date in a date range"""
def tick_list(symbol, span='week'): #date_range takes in array of 2 dates [date1, date2]; return list of delta from date1 to date 2
    price_list = pd.DataFrame()
    historicals = robin.stocks.get_historicals(symbol, span='week', bounds='regular')
    #print(historicals)
    for h in historicals:
        h_date = h['begins_at']
        h_price = h['open_price']
        h_df = pd.Series([h_date, float(h_price)])
        #print(h_df[0])
        #pd.concat([price_list, h_df])
        price_list = price_list.append(h_df, ignore_index=True)
    return price_list

    #print(price_list)
    #for span of 'day' with extended bounds, ticker every 5 minutes from beginning of day
    #for span of 'week' with regular bounds, ticker every 10 minutes
    '''date = date1
    while date <= date2:
        date_price =
        price_list.append([date, date_price])
        date+=1'''

def moving_avg(l, b): #return list of moving averages with every b ticks
    a = 0
    #print(l[a:b])
    avgs = pd.Series(mean(l[a:b][1]))
    while b < len(l):
        a+=1
        b+=1
        avg = pd.Series(mean(l[a:b][1]))
        avgs = avgs.append(avg)
    avgs = avgs.reset_index()
    avgs = avgs.drop(columns='index')
    return avgs

def delta_list(symbol, span='week'):
    ticks = tick_list(symbol, span)
    smoothed = moving_avg(ticks, b=6)
    deltas = pd.Series()
    a = 0
    while a+1 < len(smoothed):
        deltas = deltas.append(smoothed.iloc[a+1] - smoothed.iloc[a])
        a+=1
    deltas = deltas.reset_index()
    fig, axs = plt.subplots(2)
    fig.suptitle('Rolling avg vs. deltas:' + symbol)
    axs[0].plot(smoothed)
    axs[1].plot(deltas)
    plt.show()
    return deltas

def main():
    initial_setup()
    initial = 1
    check_portfol()
    watchlist = pd.read_csv('watchlist.csv')
    symbols = watchlist['symbol']
    for symbol in symbols:
        delta_list(symbol, span='week')
        min_check(symbol, span='week')





if __name__ == "__main__":
    main()
