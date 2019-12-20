# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:39:15 2019

@author: rohit.wardole
"""

import pandas as pd
import numpy as np
import re
from nltk.tokenize import word_tokenize

df = pd.read_csv("cropped_enron_data.csv")

df = df.fillna(' ')

Processed_email = []
def remove_common_words(email):
    for i in range(0,len(email)):
        eml = email[i]
        x = eml.replace("UNCLASSIFIED","")
        x = x.replace("CONFIDENTIAL","")
        x = x.replace("Sent","")
        x = x.replace("Subject","")
        x = x.replace("Pis print","")
        x = x.replace("FYI","")
        x = x.replace("Fyi","")
        x = x.replace("fyi","")
        x = x.replace("Cc","")
        x = x.replace("B6","")
        x = x.replace("B5","")
        x = x.replace("U.S. Department of State","")
        x = x.replace("U.S Department of State","")
        x = x.replace("STATE DEPT. - PRODUCED TO HOUSE SELECT BENGHAZI COMM.","")
        x = x.replace("SUBJECT TO AGREEMENT ON SENSITIVE INFORMATION & REDACTIONS. NO FOIA WAIVER.","")
        x = x.replace("RELEASE IN FULL","")
        x = x.replace("RELEASE IN PART","")
        x = x.replace("RELEASE IN","")
        x = x.replace("FULL","")
        x = x.replace("PART","")
        x = x.replace("Case No. F-2015-04841","")
        x = x.replace("Case No. F-2014-20439","")
        x = x.replace("RELEASE","")
        x = x.replace("IN","")
        x = x.replace("Doc No. C057","")
        x = x.replace("STATE-","")
        x = x.replace("STATE-SCB00","")
        x = x.replace("STATE-5CB00","")
        x = x.replace("Original Message","")
        x = x.replace("Forwarded by Phillip K Allen/HOU/ECT on","")
        Processed_email.append(x)

strip_common = df['message']
remove_common_words(strip_common)       
df['Processed_RawText']  = Processed_email

def parse_raw_message(raw_message):
    lines = raw_message.split('\n')
    email = {}
    message = ''
    for line in lines:
        if ':' not in line:
            message += line.strip('\n')
            email['body'] = message
    return email

def parse_into_emails(messages):
    emails = [parse_raw_message(message) for message in messages]
    return {
        'body': map_to_list(emails, 'body')
    }

def map_to_list(emails, key):
    results = []
    for email in emails:
        if key not in email:
            results.append('')
        else:
            results.append(email[key])
    return results

email_df = pd.DataFrame(parse_into_emails(df.Processed_RawText))  

cleaned_email = []
def clean_email(email):
    for i in range(0,len(email)):
        eml= email[i]
        eml = re.sub('[^a-zA-Z]',' ',str(eml))
        cleaned_email.append(eml)

strip_space = email_df['body']        
clean_email(strip_space)
email_df['Cleaned Email'] = cleaned_email

cleaned_body = []
def clean_emailbody(email):
    for i in range(0,len(email)):
        eml = email[i]
        eml = word_tokenize(eml)
        eml = ' '.join(eml)
        cleaned_body.append(eml)

eml_col = email_df['Cleaned Email']      
clean_emailbody(eml_col)  
email_df['Final_Cleaned_Email'] = cleaned_body

email_df = email_df[['Final_Cleaned_Email']]
export_csv = email_df.to_csv(r'Cleaned_Emails.csv',index=None,header=True)

