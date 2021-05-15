#necassary imports
import time 
from alpha_vantage.techindicators import TechIndicators
import requests
import os

#creating the txt file to store the data
if os.path.exists('SlowStoch Database.csv'):
    os.remove('SlowStoch Database.csv')
f = open('SlowStoch Database.csv','a')
f.write('ticker, buy date, sell date, buy price, sell price, % change, days in trade\n')
f.close()

#API key to allow my device to communsicate with the various netwroks needed 
api_key = '9WMTGK8QNAPIL5G9' #alphavantage
twelveDataAPI_key = '36f794df60cb499eb256f83d9c3661c8' #twelveDataAPI

#A list containg all the tickers of the Dow Jones Industrial Average(As of 2021)
DJStockList = ['MMM','AXP','AMGN','AAPL','BA','CAT','CVX','CSCO','KO','DIS','DOW','GS','HD','HON','IBM','INTC','JNJ','JPM','MCD','MRK','MSFT','NKE','PG','CRM','TRV','UNH','VZ','V','WBA','WMT']

print ('all imports and file creating succesful')
print ()

for stock in DJStockList:
    signal_Given = 0
    start_time = time.time()
    print (stock)
    ti = TechIndicators(key=api_key, output_format='json')
    gotMACDData = False
    while gotMACDData == False:
        try:
            dictOfMACDValuesForStock = (ti.get_stoch(symbol=stock, interval = 'daily')[0]) #gets the RSI data for every market day in a dictionary format - with day as the key and RSI as the value
            gotMACDData = True
        except OSError:
            print ('OS Error occoured -I think this is a connection based error')
            time.sleep(30)
        except:
            print ('unknow error occoured')
            x = input('press cnrtl c')

    listOfDates = (list(dictOfMACDValuesForStock.keys())[::-1]) #reverses and stores the dates as a list 
    stockOwned = False
    buyWatch = False
    sellWatch = False

    for date in listOfDates:
        currentKReading = float(((dictOfMACDValuesForStock[date])['SlowK']))
        currentDReading = float(((dictOfMACDValuesForStock[date])['SlowD']))
        # print(date, currentRSI)
        # time.sleep(0.1)

        #stock has a K reading below 20 and has thd K below the D line
        if currentKReading < 20 and currentDReading > currentKReading:
            buyWatch = True

        #stock has a K reading above 20 and it used to be below 20 and the stock also had D reading above the K reading, now the D is below the K
        if currentKReading > 20 and buyWatch == True and currentDReading < currentKReading:
            buyDate = listOfDates[listOfDates.index(date)+1]
            start_time = time.time()
            buy_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={buyDate}&end_date={buyDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            gotBuyData = False
            while gotBuyData == False:
                try:
                    buyCompleteData = requests.get(buy_stockData_url).json()
                    gotBuyData = True
                except:
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
                print ('There has',signal_Given,'signals given')
                print ('something went wrong when trying to get the buy price data - it didnt have status - ok or code 400')
            buyPrice = float(buyCompleteData['values'][0]['open'])
            buyPrice = buyPrice*0.99 #we are assuming a 1% commision/spread/stamp duty
            stockOwned = True
            buyWatch = False
            print ('---------------------------------------------------')
            print ('Buy signal')
            print ('date :',buyDate)
            print ('buy-price :',buyPrice)
            print ('---------------------------------------------------')
            if time.time() - start_time < 108:
                time.sleep(108-(time.time() - start_time))#to stop over drawing on the API and causing my system to crash
            time.sleep(10)

        #stock's K becomes overbought and 
        if currentKReading > 80 and stockOwned == True and sellWatch == False:
            sellWatch = True

        #stock is sold if it's falls below oversold or the K falls below the D
        if ((currentKReading < 80 and sellWatch == True) or (currentKReading < currentDReading)) and stockOwned == True:
            stockOwned = False
            sellWatch = False
            sellDate = listOfDates[listOfDates.index(date)+1]
            buyIndex = listOfDates.index(buyDate)
            sellIndex = listOfDates.index(sellDate)
            daysInTrade = sellIndex - buyIndex
            start_time = time.time()
            sell_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={sellDate}&end_date={sellDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            gotSoldData = False
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
            f = open('SlowStoch Database.csv','a')
            f.write(stock+','+str(buyDate)+','+str(sellDate)+','+str(buyPrice)+','+str(sellPrice)+','+str(percentage_Change)+','+str(daysInTrade)+'\n')
            f.close()
            if time.time() - start_time < 108:
                time.sleep(108-(time.time() - start_time))#to stop over drawing on the API and causing my system to crash
            time.sleep(10)