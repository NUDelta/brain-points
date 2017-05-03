
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
    """Time difference in seconds"""
    try:
        diff = abs((float(timestamp1)-float(timestamp2))*.001)
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
    keystrokes = csvToDataFrame(path_to_file)
    totalTime = 0
    timeTyping = 0
    timePaused = 0
    maxPause = 0
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
            if maxPause < timeDifference(secondTime,firstTime):
                maxPause = timeDifference(secondTime,firstTime)
            startTypingTime = secondTime
    totalTime = totalTime/60
    timeTyping = timeTyping/60
    timePaused = timePaused/60
    maxPause = maxPause/60
    return [totalTime,timeTyping,timePaused,maxPause]

def thirds(path_to_file):
    """Amount of code typed in 1st, 2nd, and 3rd chunk of coding"""
    keystrokes = csvToDataFrame(path_to_file)
    # print(keystrokes['Timestamp'].count())
    # print(float(keystrokes['Timestamp'][keystrokes['Timestamp'].count()-1])/60)
    # print(float(keystrokes['Timestamp'][0])/60)
    totalTime = timeDifference(keystrokes['Timestamp'][keystrokes['Timestamp'].count()-1],keystrokes['Timestamp'][0])
    firstThird = 0
    secondThird = 0
    lastThird = 0
    totalCode = 0
    for i in range(keystrokes['Timestamp'].count()-1):
        Key = keystrokes['Key'][i] 
        if len(Key) == 1:
            totalCode += 1
            timeDiff = timeDifference(keystrokes['Timestamp'][i],keystrokes['Timestamp'][0])
            if timeDiff < (totalTime/3):
                firstThird += 1
            elif timeDiff < (2*totalTime/3):
                secondThird += 1
            else:
                lastThird += 1
    return [firstThird/totalCode,secondThird/totalCode,lastThird/totalCode]

def deletions(path_to_file):
    """Find the number of flouries of deletions (now defined as three deletes within a span of 5 seconds)"""
    # This will miss and instance where delete2,delete3,delete4 are within 5 seconds if delete1 and delete3 are outside of 5 seconds
    keystrokes = csvToDataFrame(path_to_file)
    flouries = 0
    deletes = 0
    for i in range(keystrokes['Timestamp'].count()):
        # check if it's a delete key
        Key = keystrokes['Key'][i]
        if Key == "backspace":
            timeLastDelete = keystrokes['Timestamp'][i]
            # print(timeDifference(timeLastDelete,timeFirstDelete))
            # check if it's the first delete key (deletes = 0)
            if deletes == 0:
                # keep track of that time
                # add 1 to delete
                timeFirstDelete = keystrokes['Timestamp'][i]
                deletes += 1
            # elseif see if the time is within 5 seconds
            elif timeDifference(timeLastDelete,timeFirstDelete) <= 5:
                # add to the number of deletes
                deletes += 1
            # if the time is past 5 seconds compared to the timeFirstDelete:
            else:
                # see if the number of deletes > 3:
                if deletes >= 3:
                    # add to the number of flouries
                    flouries += 1
                # reset timeFirstDelete to the current time
                timeFirstDelete = keystrokes['Timestamp'][i]
                # reset deletes to = 1
                deletes = 1
    return flouries

def maxPausePreDeletion(path_to_file):
    """Find the longest pause before a deletion"""
    keystrokes = csvToDataFrame(path_to_file)
    maxPause = 0
    startTypingTime = keystrokes['Timestamp'][0]
    for i in range(keystrokes['Timestamp'].count()-1):
        prevTime = keystrokes['Timestamp'][i]
        Key = keystrokes['Key'][i+1]
        if Key == "backspace":
            # find the time difference 
            timeDiff = timeDifference(keystrokes['Timestamp'][i+1],prevTime)
            if timeDiff > maxPause:
                maxPause = timeDiff
    return maxPause/60

def qualCode(path_to_file):
    """Finds the number of times the participant used Google"""
    notes = csvToDataFrame(path_to_file)
    numGoogle = 0
    numTests = 0
    numTestCases = 0
    numQuestions = 0
    for i in range(notes['Key'].count()):
        if notes['Key'][i] == "google":
            numGoogle += 1
        elif notes['Key'][i] == "test case":
            numTestCases += 1
        elif notes['Key'][i] == "question":
            numQuestions += 1
        elif notes['Key'][i] == "success" or notes['Key'][i] == "fail" or notes['Key'][i] == "success" or "error" in notes['Key'][i]:
            numTests += 1
    return [numGoogle,numTests,numTestCases,numQuestions]


def createBigCSV(path_to_directory):
    """main function that compiles all calculated features into an excel spreadsheet"""
    participantIDs = getDirNames(path_to_directory)
    for Id in participantIDs:
        keystrokeFiles = getDirNames(path_to_directory + "/" + Id)
        for f in keystrokeFiles:
            if "qualcoding" not in f:
                info = pd.DataFrame()
                info['Participant'] = [Id]
                info['Problem'] = [f]
                path = path_to_directory+"/"+Id+"/" + f
                [totalTime,timeTyping,timePaused,maxPause] = times(path)
                info['Total Time'] = [totalTime]
                info['Time Typing'] = [timeTyping]
                info['Time Paused'] = [timePaused]
                info['Max Pause'] = [maxPause]
                [third1,third2,third3] = thirds(path)
                info['Code Ratio Third1'] = [third1]
                info['Code Ratio Third2'] = [third2]
                info['Code Ratio Third3'] = [third3]
                deletes = deletions(path)
                info['Deletions'] = [deletes]
                pauseDelete = maxPausePreDeletion(path)
                info['maxPausePreDeletion'] = [pauseDelete]
                [minTypingtoRunningTime,aveTypingtoRunningTime] = typingToRunningTime(path)
                info['minTypingtoRunningTime'] = minTypingtoRunningTime
                info['aveTypingtoRunningTime'] = aveTypingtoRunningTime
                [minRunningtoTypingTime,aveRunningtoTypingTime] = runningToTypingTime(path)
                info['minRunningtoTypingTime'] = minRunningtoTypingTime
                info['aveRunningtoTypingTime'] = aveRunningtoTypingTime
                numRuns = numTimesRun(path)
                info['numTimesRun'] = numRuns
                totalComments = numComments(path)
                info['numComments'] = totalComments
                lenComments = lengthOfComments(path)
                info['Comment Lengths'] = lenComments
                if (os.path.exists("keystrokeFeatures.csv")):
                    info.to_csv('keystrokeFeatures.csv', mode='a', index=False, header=False)
                else:
                    info.to_csv('keystrokeFeatures.csv', index=False, header=True)
            # if "qualcoding" in f:
            #     infoQual = pd.DataFrame()
            #     infoQual['Participant'] = [Id]
            #     infoQual['Problem'] = [f]
            #     path = path_to_directory+"/"+Id+"/" + f
            #     [numGoogle,numTests,numTestCases,numQuestions] = qualCode(path)
            #     infoQual['numGoogle'] = [numGoogle]
            #     infoQual['numTests'] = [numTests]
            #     infoQual['numTestCases'] = [numTestCases]
            #     infoQual['numQuestions'] = [numQuestions]
            #     if (os.path.exists("qualFeatures.csv")):
            #         infoQual.to_csv('qualFeatures.csv', mode='a', index=False, header=False)
            #     else:
            #         infoQual.to_csv('qualFeatures.csv', index=False, header=True)
                





def typingToRunningTime(path_to_file):
    """min time between typing and running"""
    keystrokes = csvToDataFrame(path_to_file)
    minimum = float("inf")
    sumation = 0
    count = 0
    average=0

    for i in range(keystrokes['Key'].count()-1):
        firstKey = keystrokes['Key'][i]
        secondKey = keystrokes['Key'][i+1]
        firstTime = keystrokes['Timestamp'][i]
        secondTime = keystrokes['Timestamp'][i+1]
        tempTimeDiff = timeDifference(secondTime,firstTime)
        
        if secondKey == "cmd-i":
            if tempTimeDiff<minimum:
                minimum = tempTimeDiff
            sumation=sumation+tempTimeDiff
            count= count + 1
    
    if(count == 0):
        minimum="never ran code"
    else:
        average=sumation/count

    # return ["before running", "minimum: " + str(minimum), 
    #         "average: " + str(average), 
    #         "count: " + str(count)]
    return [minimum,average] 


def runningToTypingTime(path_to_file):
    """min time between running and typing"""
    keystrokes = csvToDataFrame(path_to_file)
    minimum = float("inf")
    sumation = 0
    count = 0
    average = 0

    for i in range(keystrokes['Key'].count()-1):
        firstKey = keystrokes['Key'][i]
        secondKey = keystrokes['Key'][i+1]
        firstTime = keystrokes['Timestamp'][i]
        secondTime = keystrokes['Timestamp'][i+1]
        tempTimeDiff = timeDifference(secondTime,firstTime)
        
        if firstKey == "cmd-i":
            if tempTimeDiff<minimum:
                minimum = tempTimeDiff
            sumation=sumation+tempTimeDiff
            count= count + 1

    if(count!= 0):
        average = sumation/count

    #last key is cmd-i
    if secondKey == "cmd-i":
        count= count + 1

    if(count == 0):
        minimum = "never ran code"

    # return ["after running", "minimum: " + str(minimum), 
    #         "average: " + str(average),
    #         "count: " + str(count)]
    return [minimum, average]

def numTimesRun(path_to_file):
    """Number of times code was run"""
    keystrokes = csvToDataFrame(path_to_file)
    count = 0
    for i in range(keystrokes['Key'].count()):
        Key = keystrokes['Key'][i]
        if Key == "cmd-i":
            count= count + 1
    return count

def numComments(path_to_file):
    """Number of times code was run"""
    keystrokes = csvToDataFrame(path_to_file)
    count = 0
    for i in range(keystrokes['Key'].count()):
        Key = keystrokes['Key'][i]
        if Key == "#":
            count= count + 1
    return count

def lengthOfComments(path_to_file):
    """Number of times code was run"""
    keystrokes = csvToDataFrame(path_to_file)
    total = 0
    flag = False

    for i in range(keystrokes['Key'].count()):
        Key = keystrokes['Key'][i]
        if Key == "#":
            flag = True
        if len(Key) == 1 and flag == True:
            total +=1
        if Key == "enter":
            flag == False

    return total


# path = "Study1/Participant 6/keystrokes1.csv"

# print typingToRunningTime(path)
# print numComments(path)
# print lengthOfComments(path)
# print runningToTypingTime(path)
createBigCSV("/Users/morganwalker/Desktop/Spring 2017/DTR/brain-points/Feature Calculations/Study 1")