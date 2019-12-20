# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 14:45:35 2019

@author: rohit.wardole
"""
import pandas as pd
import numpy as np
import re
from nltk.tokenize import word_tokenize


df = pd.read_csv("cropped_enron_data.csv")

#df = df[['RawText']]

df = df.fillna(' ')

#single_line_col = []
#def get_in_one_line(email):
#    for i in range(0,len(email)):
#        eml = email[i]
#        x = eml.replace("\n","\t")
#        single_line_col.append(x)
#
#single_line = df['RawText']
#get_in_one_line(single_line)       
#
#df['One line']  = single_line_col

strip_unclassified_col = []
def remove_unclassified(email):
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
        x = x.replace("STATE-5CB00","")
        x = x.replace("Original Message","")
        x = x.replace("Forwarded by Phillip K Allen/HOU/ECT on","")
        strip_unclassified_col.append(x)

strip_unclassified = df['message']
remove_unclassified(strip_unclassified)       
df['Processed_RawText']  = strip_unclassified_col
    

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

rev_col = email_df['body']        
clean_email(rev_col)
email_df['Cleaned Email'] = cleaned_email

cleaned_body = []
def clean_emailbody(email):
    for i in range(0,len(email)):
        eml = email[i]
        eml = eml.replace("SCB","")
        eml = eml.replace("CB","")
        eml = eml.replace("docx","")
        eml = word_tokenize(eml)
        eml = ' '.join(eml)
        cleaned_body.append(eml)

eml_col = email_df['Cleaned Email']      
clean_emailbody(eml_col)  
email_df['Final_Cleaned_Email'] = cleaned_body


email_df = email_df[['Final_Cleaned_Email']]
export_csv = email_df.to_csv(r'Enron_Cleaned_Emails.csv',index=None,header=True)

df = df[['message']]
export_csv = df.to_csv(r'Enron_RawText.csv',index=None,header=True)
