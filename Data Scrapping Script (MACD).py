#This part of code imports some code modules that allow my code to use mods for python that allow my program to fancier things
#This includes setting time delays, pulling data from alpha_vantage and so forth 
import time 
from alpha_vantage.techindicators import TechIndicators
import requests
import os

#This checks to see if a MACD database file already exsisted and if it does it deletes it. 
#This was helpful when developing this software as it means I didn't have to manually delete the database every time which would have been time consuming
if os.path.exists('MACD Database.csv'):
    os.remove('MACD Database.csv')
f = open('MACD Database.csv','a')

#This writes headers to the database which is useful for me as it allows me to keep better track of each column in my databse
#This makes sure I dont make any mistakes when pulling from and pushing to the database
f.write('ticker, buy date, sell date, buy price, sell price, % change, days in trade\n')

#Clsoes the file as only having a file open for too long can lead to file courpution and is just a bad idea
f.close()

#defining variables with API keys I got from the respective website of AlphaVantage and Twelve data
# These API keys allow my computer to communicate with the various networks needed to get the data I want  
api_key = '3463dfs41034vsd7139fdfs8049' #Not my API key but my API key would look like this. 
twelveDataAPI_key = '3473814913yi4rh3jo4pry23tgh41341' #All an API key does is identify my device and therefore allow the various API providers to charge me (if I went over their limits)

#defining a variable to be used determine how many signals the stratagy gave. 
#This allowed me to make an estimate on how long the script would need to run
signal_Given = 0  

#A list containg all the tickers of the Dow Jones Industrial Average(As of 2021)
DJStockList = ['MMM','AXP','AMGN','AAPL','BA','CAT','CVX','CSCO','KO','DIS','DOW','GS','HD','HON','IBM','INTC','JNJ','JPM','MCD','MRK','MSFT','NKE','PG','CRM','TRV','UNH','VZ','V','WBA','WMT']

#This displays the words in speech marks to the screen and then adds a blank line
#This is useful from a development point of view as it measn I can easily tell if my program has started running succesfully
print ('all imports and file creating succesful')
print ()

#This starts a loop whereby the following code is run for each stock mentioned in the list above
for stock in DJStockList:
    #gets the current time since 00:00 01/01/1970. This is known as the epoch and basically a computer (probably in san francisco) updates a value known as the epoch value every second
    #This data can be stored locally and not changed as shown below - this allows for accurate time delays to be made as my system can figure out how much time it took to complete the data pull 
    start_time = time.time()
    
    #prints the ticker symbol of a stock so I know how far through the program my device is 
    print (stock)

    #Creates an object within the class TechIndicators (a bit complicated for non comp sci people)
    ti = TechIndicators(key=api_key, output_format='json')

    #defines a variable that can be used to check if data for the price of a given stock has been got/pulled
    gotMACDData = False
    
    #gets the MACD data retrying it it fails using the gotMACDData as a query for failing the pull the said data
    while gotMACDData == False:
        try:
            dictOfMACDValuesForStock = (ti.get_macd(symbol=stock, interval = 'daily', series_type = 'close')[0]) #gets the RSI data for every market day in a dictionary format - with day as the key and RSI as the value
            gotMACDData = True

        #If there is an internet outage the program doesnt crash instead it waits 30 seconds and tries again
        except OSError:
            print ('OS Error occoured - I think this is a connection based error')
            time.sleep(30)

        #If an unknow error occours I press ctrl + c to stop the program and find a soultion for the error (this is useful for debugging) 
        except:
            print ('unknow error occoured')
            x = input('press cnrtl c')

    #formats the pulled stock price data in a more useful way for my program
    listOfDates = (list(dictOfMACDValuesForStock.keys())[::-1])

    #defines a few variables that are to authentaicte buy and sell signals
    stockOwned = False
    prevNegHist = False
    prevPosHist = False

    #iterates over the list of dates my system got price data for and gets the MACD indactor data for each of these dates
    for date in listOfDates:
        currentMACDHistReading = float(((dictOfMACDValuesForStock[date])['MACD_Hist']))
        currentMACDLineReading = float(((dictOfMACDValuesForStock[date])['MACD']))

        #if the histogram of the MACD indicator is red then the stock is put on a watchlist effectivly 
        if currentMACDHistReading < 0 and prevNegHist == False:
            prevNegHist = True

        #if the stock then has a green histogram then my program simulates it being bought
        if currentMACDHistReading > 0 and stockOwned == False and prevNegHist == True and currentMACDLineReading < 0:
            buyDate = listOfDates[listOfDates.index(date)+1]
            start_time = time.time()
            buy_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={buyDate}&end_date={buyDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            
            #All this code does is validates that the stock price data was succesfully pulled and if so it assigns it to the appropriate variable
            gotBuyData = False
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

            #This codes simualates the 1% commision I spoke about earlier
            buyPrice = buyPrice*1.01 
            stockOwned = True
            prevNegHist = False

            #outputs some words stating what has happened to the screen this is mainly so I know my program hasnt crashed 
            print ('---------------------------------------------------')
            print ('Buy signal')
            print ('date :',buyDate)
            print ('buy-price :',buyPrice)
            print ('---------------------------------------------------')

            #Adds a delay of 110 seconds minus the time is took to pull the data above is added
            #This is to stop me from accidently paying my API providers
            if time.time() - start_time < 110:
                time.sleep(110-(time.time() - start_time))#to stop over drawing on the API and causing my system to crash

        #The stock is put on a sell watchlist 
        if currentMACDHistReading > 0 and stockOwned == True and prevPosHist == False:
            prevPosHist = True

        #if the stock's histogram reading goes negative or red then is is sold
        if currentMACDHistReading < 0 and prevPosHist == True and stockOwned == True:
            stockOwned = False
            prevPosHist = False
            sellDate = listOfDates[listOfDates.index(date)+1]
            buyIndex = listOfDates.index(buyDate)
            sellIndex = listOfDates.index(sellDate)
            daysInTrade = sellIndex - buyIndex
            start_time = time.time()
            sell_stockData_url = f'https://api.twelvedata.com/time_series?symbol={stock}&start_date={sellDate}&end_date={sellDate}&interval=1day&outputsize=12&apikey={twelveDataAPI_key}'
            
            #All this code does is validate that a valid sell price could be obtained by my program and if so the values are assinged to the appropraite variables
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

            #works out the percentage change of the trade that just occoured
            percentage_Change = ((sellPrice/buyPrice)-1)*100

            #outputs words stating the stock has been 'sold' to the screen - this is mainly so I know my program hasnt crashed
            print ('---------------------------------------------------')
            print ('Sell signal')
            print ('date :',sellDate)
            print ('sell-price :',sellPrice)
            print ('days in trade :',daysInTrade)
            print ('percentage change :', (str(percentage_Change)+str('%')))
            print ('---------------------------------------------------')
            
            #writes the data for each trade to the MACD database, where it is later read and interpretted by my data analysis script
            f = open('MACD Database.csv','a')
            f.write(stock+','+str(buyDate)+','+str(sellDate)+','+str(buyPrice)+','+str(sellPrice)+','+str(percentage_Change)+','+str(daysInTrade)+'\n')
            f.close()

            #adds a delay to stop me overdrawing on my API and paying money to my API providers
            if time.time() - start_time < 110:
                time.sleep(110-(time.time() - start_time))