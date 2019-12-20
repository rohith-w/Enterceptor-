# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 12:31:30 2019

@author: rohit.wardole
"""

import tweepy
import datetime
import xlsxwriter
import sys

# credentials from https://apps.twitter.com/
consumerKey = "uoDSJuXXORzdESUoqvul6nMal"
consumerSecret = "ONsA4H3neyhYAZyXMIBuvSUZ90zvl6Csq6orogL1H0bkeSIuzv"
accessToken = "838028901548969984-B97MYC1foGXma6D9AJIgPuazh2v3AqO"
accessTokenSecret = "drlniznAE1lnvUiy2pw78Ro3i3mjoLrFltNK18hKdVGTL"

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
     
api = tweepy.API(auth)

username = '@censusAmericans'
startDate = datetime.datetime(2019, 12, 4, 0, 0, 0)
endDate =   datetime.datetime(2019, 12, 10, 0, 0, 0)

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

workbook = xlsxwriter.Workbook(username + ".xlsx")
worksheet = workbook.add_worksheet()
row = 0
for tweet in tweets:
    worksheet.write_string(row, 0, str(tweet.author.id))
    worksheet.write_string(row, 1, str(tweet.created_at))
    worksheet.write(row, 2, tweet.text)
    worksheet.write_string(row, 3, str(tweet.in_reply_to_status_id))
    row += 1

workbook.close()
print("Excel file ready")


#import pandas as pd
#
#df = pd.read_excel("@simpscreens.xlsx",header=None)
#
#df = df.drop_duplicates()
#
#export_excel = df.to_excel (r'@simpscreens.xlsx', index = None, header=True)