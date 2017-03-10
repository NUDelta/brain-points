# number of lines
# number of characters
# ratio of backspaces
# ratio of comments
# average time between typing
# flurries of typing (were they deleted)?

# not answered
# how do you know if they delete a whole line
# how do you know where they have moved on the page
# how do you know if they run it
# what they google

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import linear_model, datasets


def csvToDataFrame(path_to_file):
    pointCloudData = []
    data = open(path_to_file).readlines()
    for row in data:
        row = [x.rstrip() for x in row.split(',')]
        pointCloudData.append(row)
    df = pd.DataFrame(pointCloudData)
    return df

df=csvToDataFrame('keystrokes_saved.csv')
x,y=df.shape

num_lines=x
backspace=0
enter = 0
comment = 0
av_time=0

for i in range(x):
	for j in range(2):
		if(j==0):
			av_time += float(df.ix[i,j])
		if(j==1):
			if df.ix[i,j] == 'backspace':
				backspace+=1
			if df.ix[i,j] == 'enter':
				enter+=1
			if df.ix[i,j] == '#':
				comment+=1
av_time=av_time/num_lines
print av_time