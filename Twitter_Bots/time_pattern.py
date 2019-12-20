# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 09:56:12 2019

@author: rohit.wardole
"""
import tweepy
import datetime
import xlsxwriter
import sys
import pandas as pd
import datetime

username = input("Enter desired username:  ")

date_entry = input('Enter the start date in YYYY-MM-DD format:  ')
year, month, day = map(int, date_entry.split('-'))
startDate = datetime.datetime(year, month, day)

date_entry = input('Enter a end date in YYYY-MM-DD format:  ')
year, month, day = map(int, date_entry.split('-'))
endDate = datetime.datetime(year, month, day)

import time
start_time = time.time()

# credentials from https://apps.twitter.com/
consumerKey = "uoDSJuXXORzdESUoqvul6nMal"
consumerSecret = "ONsA4H3neyhYAZyXMIBuvSUZ90zvl6Csq6orogL1H0bkeSIuzv"
accessToken = "838028901548969984-B97MYC1foGXma6D9AJIgPuazh2v3AqO"
accessTokenSecret = "drlniznAE1lnvUiy2pw78Ro3i3mjoLrFltNK18hKdVGTL"

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
     
api = tweepy.API(auth)

#username = '@censusAmericans'
#startDate = datetime.datetime(2019, 12, 9, 0, 0, 0)
#endDate =   datetime.datetime(2019, 12, 10, 0, 0, 0)

tweets = []
tmpTweets = api.user_timeline(username)
for tweet in tmpTweets:
    if tweet.created_at < endDate and tweet.created_at > startDate:
        tweets.append(tweet)

while (tmpTweets[-1].created_at > startDate):
    print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
    tmpTweets = api.user_timeline(username, max_id = tmpTweets[-1].id)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)
            
df = pd.DataFrame()

User_ID = []
Date_time = []
Tweet = []
for tweet in tweets:
    User_ID.append(tweet.author.id)
    Date_time.append(str(tweet.created_at))  
    Tweet.append(tweet.text)

df['User_ID'] = User_ID
df['Date_time'] = Date_time
df['Tweet'] = Tweet           

time_list = df["Date_time"]

time_difference = []
time_difference_inSecs = []
for i in range(len(time_list)-1):
    datetimeFormat = '%Y-%m-%d %H:%M:%S'
    time1 = time_list[i]
    time2 = time_list[i+1]
    elapsed_time = datetime.datetime.strptime(time1, datetimeFormat)- datetime.datetime.strptime(time2, datetimeFormat)
    print("Difference:", elapsed_time)
    print("Days:", elapsed_time.days)
    print("Seconds:", elapsed_time.seconds)
    print("\n")
    time_difference.append(elapsed_time)
    time_difference_inSecs.append(elapsed_time.seconds)

import statistics
Bot_median = statistics.median(time_difference_inSecs)

check_bot = []
Bot = 0
Human = 0
for i in range(0,len(time_difference_inSecs)):
    if Bot_median-200 <= time_difference_inSecs[i] <= Bot_median+200:
        is_bot = 'Bot'
        Bot = Bot + 1
        check_bot.append(is_bot)
    else:
        is_interrupt = 'Human'
        Human = Human + 1
        check_bot.append(is_interrupt)
        
Test_bot_df = pd.DataFrame()        
Test_bot_df['time_difference_inSecs'] = time_difference_inSecs
Test_bot_df['check_bot'] = check_bot

if Bot > Human:
    print("Identified user posts around every " + str(Bot_median) + " seconds (approx). Hence, the user observed is a Bot.")
else:
    print("Identified Time Pattern has more variance. Hence, the user observed is a Human.")    


print("--- %s seconds ---" % (time.time() - start_time))    




"""
df["is_bot"] = 'Bot'
y_pred = df["is_bot"]
y_pred = df.iloc[0:1439,4]
y_test = Test_bot_df['check_bot']

from sklearn.metrics import accuracy_score
print('accuracy :',accuracy_score(y_test,y_pred)*100) 

from sklearn.metrics import confusion_matrix 
cm = confusion_matrix(y_test, y_pred)
#for j in range(Bot_median-100,Bot_median+100):
#    print(j)    

df_Bot = pd.read_excel("@tinycarebot.xlsx")
df_Human = pd.read_excel("@cnnbrk.xlsx")

df_Bot["is_bot"] = 'Bot'
df_Human["is_bot"] = 'Human'

result_df = pd.concat([df_Bot,df_Human])
export_excel = result_df.to_excel(r'twitter.xlsx', index = None, header=True)

#df = df.sample(frac=1).reset_index(drop=True)
#df_Bot = df_Bot.iloc[:,:]
#df_Bot = df_Bot.reset_index(drop = True)
"""