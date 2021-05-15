#Imports some modules that allowd my code to do cool stuff like changing the current working directory (cwd) of my device
import os
import pathlib
import csv

#creates a dictionary (a special computer science data structure) that allows data to be pulled from it given a specifc input
#dict_of_Database_Names[MACD] returns 'MACD Database.csv'
dict_of_Database_Names = {'MACD':'MACD Database.csv','RSI':'RSI Database.csv','Slowstoch':'SlowStoch Database.csv'}

#sets the path that my computer is working in (cwd) to that of the file - this allows my program to easily navigate through folders in the progrma
current_path = pathlib.Path(__file__).parent.absolute()
os.chdir(current_path)

#creates a list of folders in the cwd (this list is RSI,MACD and SlowStoch - I just overengingered this part)
listOfFolders = os.listdir('.')
for fileName in os.listdir('.'):
    if '.' in fileName:
        listOfFolders.remove(fileName)

#For each folder in the cwd the following code is run
for folder in listOfFolders:
    #the cwd is changed to that of the folder that this code in being run in relation to
    os.chdir(str(current_path)+'\\'+str(folder))

    #retrives the data from the appropraite database using the folder name and the dictionary mentioned above to refereence the correct file
    with open(dict_of_Database_Names[folder]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\n')
        
        #defines variables to be used later in the program
        totalDaysInTrades = 0
        line_count = 0
        totalPercentageChange = 0
        
        # each trade in the database the following code is run
        for row in csv_reader:

            #this skips the first line as the first line has column headers and they would break my code
            if line_count == 0:
                line_count = 'not first line'

            #Adds the time in the trade (in days) and the percentage change of the trade to total value of each of these variables 
            else:
                row = row[0].split(',')
                totalPercentageChange = totalPercentageChange + float(row[5])
                totalDaysInTrades = totalDaysInTrades + int(row[6])
        
        #works out the average daily change for each stratagey
        average_daily_change = totalPercentageChange ** (1/totalDaysInTrades)

        #using the average daily change for each stratagy the average daily, average yearly and total percentage changes are displayed
        print (folder + 'average daily change =', str((average_daily_change*100)-100) + str('%'))
        print(folder + 'average yearly change =',str(((average_daily_change**253)*100)-100) + str('%'))
        print(folder + 'total change =', str((((average_daily_change**253)**21)*100)-100) + str('%'))

    #returns the cwd to the root directory this allows the next iteration of the loop to continue in the correct place
    os.chdir('..')
 