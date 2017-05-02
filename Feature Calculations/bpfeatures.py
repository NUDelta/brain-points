
import os
import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import csv
import numpy as np

def getDirNames(path_to_directory):
    names = os.listdir(path_to_directory)
    names.remove('.DS_Store')
    return names

def csvToDataFrame(path_to_file):
    csvData = []
    data = open(path_to_file).readlines()
    for row in data:
        row = [x.rstrip() for x in row.split(',')]
        csvData.append(row)
    df = pd.DataFrame(csvData)
    if 2 in df.columns:
        del df[2]
    df.columns = ['Timestamp','Key']
    return df

def timeDifference(timestamp1, timestamp2):
    try:
        diff = abs((int(timestamp1)-int(timestamp2))*.001)
        return diff
    except:
        print("invalid")
        return 0
    # return 

def isEarlier(timestamp1, timestamp2):
    if '"' in timestamp1:
        timestamp1 = timestamp1.replace('"','')
    if '"' in timestamp2:
        timestamp2 = timestamp2.replace('"', '')
    date1 = datetime.utcfromtimestamp(float(timestamp1)).strftime('%Y-%m-%d')
    date2 = datetime.utcfromtimestamp(float(timestamp2)).strftime('%Y-%m-%d')
    return date1 < date2

def times(path_to_file):
    """calculate the total amount of time spent overall, typing, and paused in minutes"""
    print(path_to_file)
    keystrokes = csvToDataFrame(path_to_file)
    totalTime = 0
    timeTyping = 0
    timePaused = 0
    startTypingTime = keystrokes['Timestamp'][0]
    for i in range(keystrokes['Timestamp'].count()-1):
        firstTime = keystrokes['Timestamp'][i]
        secondTime = keystrokes['Timestamp'][i+1]
        tempTimeDiff = timeDifference(secondTime,firstTime)
        totalTime += tempTimeDiff
        # if the difference in time is greater than 15 seconds then it's considered a pause
        if tempTimeDiff > 15:
            timeTyping += timeDifference(firstTime,startTypingTime)
            timePaused += timeDifference(secondTime,firstTime)
            startTypingTime = secondTime
    totalTime = totalTime/60
    timeTyping = timeTyping/60
    timePaused = timePaused/60
    return [totalTime,timeTyping,timePaused]

def createBigCSV(path_to_directory):
    """main function that compiles all calculated features into an excel spreadsheet"""
    participantIDs = getDirNames(path_to_directory)
    for Id in participantIDs:
        keystrokeFiles = getDirNames(path_to_directory + Id)
        for f in keystrokeFiles:
            [totalTime,timeTyping,timePaused] = times(path_to_directory+Id+"/" + f)
            print([totalTime,timeTyping,timePaused])
        #     break
        # break

            # if (os.path.exists("bigFile.csv")):
            #     labels.to_csv('bigFile.csv', mode='a', index=False, header=False)
            # else:
            #     labels.to_csv('bigFile.csv', index=False, header=True)

createBigCSV("/Users/morganwalker/Desktop/Spring 2017/DTR/Study 1/")