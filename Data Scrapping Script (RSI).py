#necassary imports
import time 
from alpha_vantage.techindicators import TechIndicators
import requests
import os

#creating the txt file to store the data
if os.path.exists('RSI Database.csv'):
    os.remove('RSI Database.csv')
f = open('RSI Database.csv','a')
f.write('ticker, buy date, sell date, buy price, sell price, % change, days in trade\n')
f.close()

#API key to allow my device to communsicate with the various netwroks needed 
api_key = '9WMTGK8QNAPIL5G9' #alphavantage
twelveDataAPI_key = '36f794df60cb499eb256f83d9c3661c8' #twelveDataAPI

signal_Given = 0

#A list containg all the tickers of the Dow Jones Industrial Average(As of 2021)
DJStockList = ['MMM','AXP','AMGN','AAPL','BA','CAT','CVX','CSCO','KO','DIS','DOW','GS','HD','HON','IBM','INTC','JNJ','JPM','MCD','MRK','MSFT','NKE','PG','CRM','TRV','UNH','VZ','V','WBA','WMT']

print ('all imports and file creating succesful')
print ()

for stock in DJStockList:
    start_time = time.time()
    print (stock)
    ti = TechIndicators(key=api_key, output_format='json')
    gotRSIData = False
    while gotRSIData == False:
        try:
            dictOfRSIValuesForStock = (ti.get_rsi(symbol=stock, interval = 'daily', time_period = 14, series_type = 'close')[0]) #gets the RSI data for every market day in a dictionary format - with day as the key and RSI as the value
            gotRSIData = True
        except OSError:
            print ('OS Error occoured -I think this is a connection based error')
            time.sleep(30)
        except:
            print ('unknow error occoured')
            x = input('press cnrtl c')

    listOfDates = (list(dictOfRSIValuesForStock.keys())[::-1]) #reverses and stores the dates as a list 

    stockOwned = False
    previouslyOverSold = False
    previouslyOverBought = False

    for date in listOfDates:
        currentRSI = float(((dictOfRSIValuesForStock[date])['RSI']))
        # print(date, currentRSI)
        # time.sleep(0.1)

        #stock becomes oversold
        if currentRSI < 30 and previouslyOverSold == False:
            previouslyOverSold = True

        #stock is bought upon RSI rising above 30 
        if currentRSI > 30 and stockOwned == False and previouslyOverSold == True:
            buyDate = listOfDates[listOfDates.index(date)+1]
            start_time = time.time()
            buy_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={buyDate}&end_date={buyDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            gotBuyData = False
            signal_Given = signal_Given + 1
            while gotBuyData == False:
                try:
                    buyCompleteData = requests.get(buy_stockData_url).json()
                    gotBuyData = True
                except :
                    print ('An unknow error occoured while trying to get stocks buy price')
                    time.sleep(30)
            if buyCompleteData['status'] == 'ok':
                sellPrice = float(buyCompleteData['values'][0]['open'])
            elif buyCompleteData['code'] == 400 and buyCompleteData['status'] == 'error':
                print (buyCompleteData)
                print ('an error occoured while trying to convert the buy data to an single price - suspected that data was not avaliable for that date, this error has been handled (suppposdely)')
                print ('date :',date)
                print ('ticker :',stock)
                print ('There were',signal_Given,'signals given')
                break
            else:
                print (buyCompleteData)
                print ('datet :',date)
                print ('ticker :',stock)
                print ('There were',signal_Given,'signals given')
                print ('something went wrong when trying to get the buy price data - it didnt have status - ok or code 400')
            buyPrice = float(buyCompleteData['values'][0]['open'])
            buyPrice = buyPrice*0.99 #we are assuming a 1% commision/spread/stamp duty
            stockOwned = True
            previouslyOverSold = False
            print ('---------------------------------------------------')
            print ('Buy signal')
            print ('date :',buyDate)
            print ('buy-price :',buyPrice)
            print ('---------------------------------------------------')
            if time.time() - start_time < 110:
                time.sleep(110-(time.time() - start_time))#to stop over drawing on the API and causing my system to crash

        #stock becomes overbought
        if currentRSI > 70 and stockOwned == True and previouslyOverBought == False:
            previouslyOverBought = True

        #stock is sold
        if currentRSI < 70 and previouslyOverBought == True and stockOwned == True:
            stockOwned = False
            previouslyOverBought = False
            sellDate = listOfDates[listOfDates.index(date)+1]
            buyIndex = listOfDates.index(buyDate)
            sellIndex = listOfDates.index(sellDate)
            daysInTrade = sellIndex - buyIndex
            start_time = time.time()
            sell_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={sellDate}&end_date={sellDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            gotSoldData = False
            signal_Given = signal_Given + 1
            while gotSoldData == False:
                try:
                    sellCompleteData = requests.get(sell_stockData_url).json()
                    gotSoldData = True
                except:
                    print ('An unknow error occoured while trying to get stocks sell price')
                    time.sleep(30)

            if sellCompleteData['status'] == 'ok':
                sellPrice = float(sellCompleteData['values'][0]['open'])
            elif sellCompleteData['code'] == 400 and sellCompleteData['status'] == 'error':
                print (sellCompleteData)
                print ('an error occoured while trying to convert the sell data to an single price - suspected that data was not avaliable for that date, this error has been handled (suppposdely)')
                print ('datet :',date)
                print ('ticker :',stock)
                print ('There were',signal_Given,'signals given')
                break
            else:
                print (sellCompleteData)
                print ('datet :',date)
                print ('ticker :',stock)
                print ('There were',signal_Given,'signals given')
                print ('unknown error occoured')
            # sellPrice = float(sellCompleteData['values'][0]['open'])
            percentage_Change = ((sellPrice/buyPrice)-1)*100
            print ('---------------------------------------------------')
            print ('Sell signal')
            print ('date :',sellDate)
            print ('sell-price :',sellPrice)
            print ('days in trade :',daysInTrade)
            print ('percentage change :', (str(percentage_Change)+str('%')))
            print ('---------------------------------------------------')
            ### ticker, buy date, sell date, buy price, sell price, % change, days in trade ### \n
            f = open('RSI Database.csv','a')
            f.write(stock+','+str(buyDate)+','+str(sellDate)+','+str(buyPrice)+','+str(sellPrice)+','+str(percentage_Change)+','+str(daysInTrade)+'\n')
            f.close()
            if time.time() - start_time < 110:
                time.sleep(110-(time.time() - start_time))#to stop over drawing on the API and causing my system to crash
