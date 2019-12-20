from flask import Flask, request, make_response
import jwt
import datetime
from functools import wraps
from flask import jsonify
import json
import collections
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eternussolutions'
import pyodbc
from flask_cors import  CORS, cross_origin

cors = CORS(app)
app.config['CORS_HEADERS'] = 'content-type'


conn = pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};'
                      r'SERVER=192.168.101.20;'
                      r'DATABASE=RelianceDemo;'
                      r'UID=SA;'
                      r'PWD=espl@123')

cursor = conn.cursor()

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        print(request.headers['x-access-token'])
#        token = request.args.get('token')
        token=request.headers['x-access-token']
        
        if not token:
            return jsonify({"Message": "Token is missing"}) , 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({"Message": "Invalid Token"}), 403
        
        return f(*args,**kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password == "espl@1234":
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 15)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response("Could not verify your login!",401,{'WWW-Authenticate' : 'Basic realm = "Login Required"'})
         
@app.route('/api/card_data', methods = ['GET'])
#@token_required
def all_data():
    output_dictionary = {}
    
    """Positive Count"""
    positive_call_result = 0
    cursor.execute("Select Count(Id) from [dbo].[tblCalls] where classification = 'Positive'")    
    for row in cursor.fetchall():
        positive_call_result = row[0]
    output_dictionary["Positive_call_count"] = positive_call_result
        
    """Negative Count"""    
    negative_call_result = 0
    cursor.execute("Select Count(Id) from [dbo].[tblCalls] where classification = 'Negative'")
    for row in cursor.fetchall():
        negative_call_result = row[0]
    output_dictionary["Negative_call_result"] = negative_call_result    
    
    """Neutral Count"""
    neutral_call_result = 0
    cursor.execute("Select Count(Id) from [dbo].[tblCalls] where classification = 'Neutral'")
    for row in cursor.fetchall():
        neutral_call_result = row[0]
    output_dictionary["Neutral_call_result"] = neutral_call_result    
        
    """Complaint Count"""
    complaint_call_result = 0
    cursor.execute("Select count(Id) from [dbo].[tblCalls] where category = 'Complaint'")
    for row in cursor.fetchall():
        complaint_call_result = row[0]
    output_dictionary["Complaint_call_result"] = complaint_call_result    
    
    """Query Count"""
    query_call_result = 0
    cursor.execute("Select count(Id) from [dbo].[tblCalls] where category = 'Query'")
    for row in cursor.fetchall():
        query_call_result = row[0]
    output_dictionary["Query_call_result"] = query_call_result    
    
    """Calls within 180secs"""
    CallsWithin_call_result = 0
    cursor.execute("Select (count(Id)* 100.0 / (Select Count(Id) From [RelianceDemo].[dbo].[tblCalls])) as Score from [RelianceDemo].[dbo].[tblCalls]  where duration <=180")
    for row in cursor.fetchall():
        CallsWithin_call_result = float(row[0])
    output_dictionary["CallsWithin_call_result"] = CallsWithin_call_result    
    
    """Average Call Duration"""
    average_call_duration = 0
    cursor.execute("Select AVG(duration) from [RelianceDemo].[dbo].[tblCalls]")
    for row in cursor.fetchall():
        average_call_duration = row[0]
    output_dictionary["Average_call_duration"] = average_call_duration
    
    """Total Count"""
    total_call_result = 0
    cursor.execute("select count(Id) from tblCalls")
    for row in cursor.fetchall():
        total_call_result = row[0]
    output_dictionary["Total_call_result"] = total_call_result
    
    """Overall Satisfaction Score"""
    overall_satisfaction_score = 0
    cursor.execute("Select AVG([sentiment_score]) from [RelianceDemo].[dbo].[tblCalls]")
    for row in cursor.fetchall():
        overall_satisfaction_score = row[0]
    output_dictionary["Overall_Satisfaction_Score"] = overall_satisfaction_score
    
    """Top 5 Agents"""
    cursor.execute("select top 5 [f-name] as Agent_Name, avg(sentiment_score) as Sentiment_Score from tblcalls left join emp on tblcalls.agent_id = emp.agent_id group by [f-name] order by avg(sentiment_score) desc ")
    objects_list = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Agent_Name'] = row.Agent_Name
        d['Sentiment_Score'] = row.Sentiment_Score
        objects_list.append(d)    
    output_dictionary["Top_5_Agents"]=objects_list
    
    """Bottom 5 Agents"""
    cursor.execute("select top 5 [f-name] as Agent_Name, avg(sentiment_score) as Sentiment_Score from tblcalls left join emp on tblcalls.agent_id = emp.agent_id group by [f-name] order by avg(sentiment_score) asc ")
    objects_list = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Agent_Name'] = row.Agent_Name
        d['Sentiment_Score'] = row.Sentiment_Score
        objects_list.append(d)    
    output_dictionary["Bottom_5_Agents"]=objects_list
    
    """Keywords"""
    cursor.execute("SELECT (len(keywords) - len(REPLACE(keywords, ' ', ''))+1) as Total_words,keywords FROM [tblCalls]")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Words'] = row.keywords
        d['Total_words'] = row.Total_words
        objects_list.append(d)
    output_dictionary["Keywords"] = objects_list
    
    """Explicit Content Count"""
    explicit_content_count = 0
    cursor.execute("Select Count(Id) as Total_Explicit_Content, [agent_id] from [RelianceDemo].[dbo].[tblCalls] where [is_explicit] = 1 group by [agent_id]")
    for row in cursor.fetchall():
        explicit_content_count = row[0]
    output_dictionary["Explicit_Content_Count"] = explicit_content_count
    
    """Explicit Content Keywords"""
    explicit_content_keywords = 0
    cursor.execute("Select keywords from [RelianceDemo].[dbo].[tblCalls] where [is_explicit] =1")
    for row in cursor.fetchall():
        explicit_content_keywords = row[0]
    output_dictionary["Explicit_Content_Keywords"] = explicit_content_keywords
    
    """Call Count by type"""
    cursor.execute("Select Count(Id) as Total_Calls, [call_category] as Call_Category from [RelianceDemo].[dbo].[tblCalls] group by [call_category]")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Calls'] = row.Total_Calls
        objects_list.append(d)
    output_dictionary["Call_Count_by_Type"] = objects_list    
    
    """Busiest Hour"""
    cursor.execute("Select FORMAT([time], 'hh') as Hour , Count(Id) as Call_Count from [RelianceDemo].[dbo].[tblCalls] group by FORMAT([time], 'hh')")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Hour'] = row.Hour
        d['Call_Count'] = row.Call_Count
        objects_list.append(d)
    output_dictionary["Busiest_Hour"] = objects_list

    """Busiest Hour by cancellation"""    
    cursor.execute("Select FORMAT([time], 'hh') as Hour , Count(Id) as Call_Count from [RelianceDemo].[dbo].[tblCalls] where call_category = 'Cancellation' group by FORMAT([time], 'hh') ")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Hour'] = row.Hour
        d['Call_Count'] = row.Call_Count
        objects_list.append(d)
    output_dictionary["Busiest_Hour_by_Cancellation"] = objects_list
    
    """Busiest Hour by Duplicate policy copy"""    
    cursor.execute("Select FORMAT([time], 'hh') as Hour , Count(Id) as Call_Count from [RelianceDemo].[dbo].[tblCalls] where call_category = 'Duplicate policy copy' group by FORMAT([time], 'hh') ")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Hour'] = row.Hour
        d['Call_Count'] = row.Call_Count
        objects_list.append(d)
    output_dictionary["Busiest_Hour_by_Duplicate_policy_copy"] = objects_list
    
    """Busiest Hour by claim health related"""    
    cursor.execute("Select FORMAT([time], 'hh') as Hour , Count(Id) as Call_Count from [RelianceDemo].[dbo].[tblCalls] where call_category = 'claim health related' group by FORMAT([time], 'hh') ")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Hour'] = row.Hour
        d['Call_Count'] = row.Call_Count
        objects_list.append(d)
    output_dictionary["Busiest_Hour_by_claim_health_related"] = objects_list
    
    """Busiest Hour by Claim under process"""    
    cursor.execute("Select FORMAT([time], 'hh') as Hour , Count(Id) as Call_Count from [RelianceDemo].[dbo].[tblCalls] where call_category = 'Claim under process' group by FORMAT([time], 'hh') ")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Hour'] = row.Hour
        d['Call_Count'] = row.Call_Count
        objects_list.append(d)
    output_dictionary["Busiest_Hour_by_Claim_under_process"] = objects_list
    
    Output_Json = json.dumps(output_dictionary)
    return Output_Json

@app.route('/api/page2_pie_chart', methods = ['GET'])
def pie_chart():
    output_dictionary = {}
    
    """Calls by Category"""
    cursor.execute("Select count(Id) as Total_Calls, category from [RelianceDemo].[dbo].[tblCalls] group by category")
    objects_list = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Category'] = row.category
        d['Total_Calls'] = row.Total_Calls
        objects_list.append(d)

    
    """Calls by Category and Complaint"""
    cursor.execute("Select Count(Id) as Total_Calls, [call_category] as Call_Category from [RelianceDemo].[dbo].[tblCalls] where category = 'Complaint' group by [call_category]")
    objects_list1 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Call_Category'] = row.Total_Calls
        objects_list1.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint"]=objects_list1
    
    """Calls by Category and Complaint and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and classification = 'Negative' group by [date]""")
    objects_list4 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list4.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Negative Sentiment"]=objects_list4 
    
    """Calls by Category and Complaint and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and classification = 'Positive' group by [date]""")
    objects_list5 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list5.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Positive Sentiment"]=objects_list5
    
    """Calls by Category and Complaint and Cancellation and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Cancellation' and classification = 'Positive' group by [date]""")
    objects_list6 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list6.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Cancellation_and_Positive Sentiment"]=objects_list6 
    
    """Calls by Category and Complaint and claim health related and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'claim health related' and classification = 'Positive' group by [date]""")
    objects_list7 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list7.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_claim_health_and_Positive Sentiment"]=objects_list7
    
    """Calls by Category and Complaint and Claim under process and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Claim under process' and classification = 'Positive' group by [date]""")
    objects_list8 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list8.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_claim_under_and_Positive Sentiment"]=objects_list8 

    """Calls by Category and Complaint and Duplicate policy copy and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Duplicate policy copy' and classification = 'Positive' group by [date]""")
    objects_list9 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list9.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_duplicate_policy_and_Positive Sentiment"]=objects_list9
    
    """Calls by Category and Complaint and Cancellation and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Cancellation' and classification = 'Negative' group by [date]""")
    objects_list10 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list10.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Cancellation_and_Negative Sentiment"]=objects_list10 
    
    """Calls by Category and Complaint and claim health related and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'claim health related' and classification = 'Negative' group by [date]""")
    objects_list11 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list11.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_claim_health_and_Negative Sentiment"]=objects_list11 
    
    """Calls by Category and Complaint and Claim under process and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Claim under process' and classification = 'Negative' group by [date]""")
    objects_list12 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list12.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_claim_under_and_Negative Sentiment"]=objects_list12 

    """Calls by Category and Complaint and Duplicate policy copy and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Complaint' and call_category = 'Duplicate policy copy' and classification = 'Negative' group by [date]""")
    objects_list13 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list13.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_duplicate_policy_and_Negative Sentiment"]=objects_list13  
    
    """Calls by Category and Complaint and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Complaint'  group by shift_of_sentiment""")
    objects_list35 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list35.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Shift_Of_Sentiments"]=objects_list35  
    
    """Calls by Category and Complaint and Claim Health Related and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Complaint' and call_category = 'claim health related' group by shift_of_sentiment""")
    objects_list36 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list36.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Claim_health_and_Shift_Of_Sentiments"]=objects_list36
    
    """Calls by Category and Complaint and Claim under process and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Complaint' and call_category = 'Claim under process' group by shift_of_sentiment""")
    objects_list37 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list37.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Claim_under_and_Shift_Of_Sentiments"]=objects_list37
    
    """Calls by Category and Complaint and Cancellation and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Complaint' and call_category = 'Cancellation' group by shift_of_sentiment""")
    objects_list38 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list38.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Cancellation_and_Shift_Of_Sentiments"]=objects_list38
    
    """Calls by Category and Complaint and Duplicate policy copy and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Complaint' and call_category = 'Duplicate policy copy' group by shift_of_sentiment""")
    objects_list39 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list39.append(d)
    objects_list[0]["Calls_by_Category_and_Complaint_and_Duplicate_policy_and_Shift_Of_Sentiments"]=objects_list39
    

    
    """Calls by Category and Information"""
    cursor.execute("Select Count(Id) as Total_Calls, [call_category] as Call_Category from [RelianceDemo].[dbo].[tblCalls] where category = 'Information' group by [call_category]")
    objects_list2 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Call_Category'] = row.Total_Calls
        objects_list2.append(d)
    objects_list[1]["Calls_by_Category_and_Information"]=objects_list2  
    
    """Calls by Category and Information and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and classification = 'Negative' group by [date]""")
    objects_list14 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list14.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Negative Sentiment"]=objects_list14 
    
    """Calls by Category and Information and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and classification = 'Positive' group by [date]""")
    objects_list15 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list15.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Positive Sentiment"]=objects_list15 
     
    """Calls by Category and Information and Cancellation and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Cancellation' and classification = 'Positive' group by [date]""")
    objects_list16 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list16.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Cancellation_and_Positive Sentiment"]=objects_list16 
    
    """Calls by Category and Information and claim health related and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'claim health related' and classification = 'Positive' group by [date]""")
    objects_list17 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list17.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_claim_health_and_Positive Sentiment"]=objects_list17 
    
    """Calls by Category and Information and Claim under process and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Claim under process' and classification = 'Positive' group by [date]""")
    objects_list18 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list18.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_claim_under_and_Positive Sentiment"]=objects_list18 

    """Calls by Category and Information and Duplicate policy copy and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Duplicate policy copy' and classification = 'Positive' group by [date]""")
    objects_list19 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list19.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_duplicate_policy_and_Positive Sentiment"]=objects_list19
    
    """Calls by Category and Information and Cancellation and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Cancellation' and classification = 'Negative' group by [date]""")
    objects_list20 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list20.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Cancellation_and_Negative Sentiment"]=objects_list20 
    
    """Calls by Category and Information and claim health related and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'claim health related' and classification = 'Negative' group by [date]""")
    objects_list21 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list21.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_claim_health_and_Negative Sentiment"]=objects_list21 
    
    """Calls by Category and Information and Claim under process and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Claim under process' and classification = 'Negative' group by [date]""")
    objects_list22 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list22.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_claim_under_and_Negative Sentiment"]=objects_list22

    """Calls by Category and Information and Duplicate policy copy and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Information' and call_category = 'Duplicate policy copy' and classification = 'Negative' group by [date]""")
    objects_list23 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list23.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_duplicate_policy_and_Negative Sentiment"]=objects_list23       

    """Calls by Category and Information and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Information'  group by shift_of_sentiment""")
    objects_list40 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list40.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Shift_Of_Sentiments"]=objects_list40 
    
    """Calls by Category and Information and Claim Health Related and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Information' and call_category = 'claim health related' group by shift_of_sentiment""")
    objects_list41 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list41.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Claim_health_and_Shift_Of_Sentiments"]=objects_list41
    
    """Calls by Category and Information and Claim under process and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Information' and call_category = 'Claim under process' group by shift_of_sentiment""")
    objects_list42 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list42.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Claim_under_and_Shift_Of_Sentiments"]=objects_list42
    
    """Calls by Category and Information and Cancellation and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Information' and call_category = 'Cancellation' group by shift_of_sentiment""")
    objects_list43 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list43.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Cancellation_and_Shift_Of_Sentiments"]=objects_list43
    
    """Calls by Category and Information and Duplicate policy copy and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Information' and call_category = 'Duplicate policy copy' group by shift_of_sentiment""")
    objects_list44 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list44.append(d)
    objects_list[1]["Calls_by_Category_and_Information_and_Duplicate_policy_and_Shift_Of_Sentiments"]=objects_list44
    
    """Calls by Category and Query"""
    cursor.execute("Select Count(Id) as Total_Calls, [call_category] as Call_Category from [RelianceDemo].[dbo].[tblCalls] where category = 'Query' group by [call_category]")
    objects_list3 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Call_Category'] = row.Total_Calls
        objects_list3.append(d)
    objects_list[2]["Calls_by_Category_and_Query"]=objects_list3
    
    """Calls by Category and Query and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and classification = 'Negative' group by [date]""")
    objects_list24 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list24.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Negative Sentiment"]=objects_list24 
    
    """Calls by Category and Query and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and classification = 'Positive' group by [date]""")
    objects_list25 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list25.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Positive Sentiment"]=objects_list25
    
    """Calls by Category and Query and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and classification = 'Positive' group by [date]""")
    objects_list26 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list26.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Positive Sentiment"]=objects_list26 
    
    """Calls by Category and Query and Cancellation and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Cancellation' and classification = 'Positive' group by [date]""")
    objects_list27 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list27.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Cancellation_and_Positive Sentiment"]=objects_list27 
    
    """Calls by Category and Query and claim health related and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'claim health related' and classification = 'Positive' group by [date]""")
    objects_list28 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list28.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_claim_health_and_Positive Sentiment"]=objects_list28 
    
    """Calls by Category and Query and Claim under process and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Claim under process' and classification = 'Positive' group by [date]""")
    objects_list29 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list29.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_claim_under_and_Positive Sentiment"]=objects_list29 

    """Calls by Category and Query and Duplicate policy copy and Positive Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Duplicate policy copy' and classification = 'Positive' group by [date]""")
    objects_list30 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list30.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_duplicate_policy_and_Positive Sentiment"]=objects_list30
    
    """Calls by Category and Query and Cancellation and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Cancellation' and classification = 'Negative' group by [date]""")
    objects_list31 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list31.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Cancellation_and_Negative Sentiment"]=objects_list31 
    
    """Calls by Category and Query and claim health related and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'claim health related' and classification = 'Negative' group by [date]""")
    objects_list32 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list32.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_claim_health_and_Negative Sentiment"]=objects_list32 
    
    """Calls by Category and Query and Claim under process and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Claim under process' and classification = 'Negative' group by [date]""")
    objects_list33 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list33.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_claim_under_and_Negative Sentiment"]=objects_list33 

    """Calls by Category and Query and Duplicate policy copy and Negative Sentiment"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [RelianceDemo].[dbo].[tblCalls]
                        where category = 'Query' and call_category = 'Duplicate policy copy' and classification = 'Negative' group by [date]""")
    objects_list34 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day'] = row.Day_of_Week
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list34.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_duplicate_policy_and_Negative Sentiment"]=objects_list34  

    """Calls by Category and Query and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Query'  group by shift_of_sentiment""")
    objects_list45 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list45.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Shift_Of_Sentiments"]=objects_list45 
    
    """Calls by Category and Query and Claim Health Related and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Query' and call_category = 'claim health related' group by shift_of_sentiment""")
    objects_list46 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list46.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Claim_health_and_Shift_Of_Sentiments"]=objects_list46
    
    """Calls by Category and Query and Claim under process and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Query' and call_category = 'Claim under process' group by shift_of_sentiment""")
    objects_list47 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list47.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Claim_under_and_Shift_Of_Sentiments"]=objects_list47
    
    """Calls by Category and Query and Cancellation and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Query' and call_category = 'Cancellation' group by shift_of_sentiment""")
    objects_list48 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list48.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Cancellation_and_Shift_Of_Sentiments"]=objects_list48
    
    """Calls by Category and Query and Duplicate policy copy and Shift Of Sentiments"""
    cursor.execute("""Select count(Id) as Count_of_sentiments, shift_of_sentiment as Shift_Of_Sentiments from [tblCalls]
                        where category = 'Query' and call_category = 'Duplicate policy copy' group by shift_of_sentiment""")
    objects_list49 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Shift_Of_Sentiments'] = row.Shift_Of_Sentiments
        d['Count_of_sentiments'] = row.Count_of_sentiments
        objects_list49.append(d)
    objects_list[2]["Calls_by_Category_and_Query_and_Duplicate_policy_and_Shift_Of_Sentiments"]=objects_list49
    
    output_dictionary["Calls_by_Category"]=objects_list
    
    Output_Json = json.dumps(output_dictionary)
    return Output_Json

@app.route('/api/page2_funnel_chart', methods = ['GET'])
def funnel_chart():
    output_dictionary = {}
    
    """Shift Of Sentiment"""
    cursor.execute("Select count(Id) Total_Sentiments, shift_of_sentiment from [RelianceDemo].[dbo].[tblCalls] group by shift_of_sentiment")
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Shift_Of_Sentiment'] = row.shift_of_sentiment
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list.append(d)
    
    """Shift Of Sentiment and Negative - Negative"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Negative - Negative'  group by category""")
    objects_list1 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list1.append(d)
    objects_list[0]["Calls_by_Category"]=objects_list1  
    
    """Shift Of Sentiment and Negative - Negative and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Negative' and classification = 'Positive' group by [date]""")
    objects_list10 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list10.append(d)
    objects_list[0]["SOS_Neg-Neg_Pos"]=objects_list10
    
    """Shift Of Sentiment and Negative - Negative and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Negative' and classification = 'Negative' group by [date]""")
    objects_list11 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list11.append(d)
    objects_list[0]["SOS_Neg-Neg_Neg"]=objects_list11
    
    
    
    """Shift Of Sentiment and Negative - Neutral"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Negative - Neutral'  group by category""")
    objects_list2 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list2.append(d)
    objects_list[1]["Calls_by_Category"]=objects_list2
    
    """Shift Of Sentiment and Negative - Neutral and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Neutral' and classification = 'Positive' group by [date]""")
    objects_list12 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list12.append(d)
    objects_list[1]["SOS_Neg-Neu_Pos"]=objects_list12
    
    """Shift Of Sentiment and Negative - Negative and Neutral Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Neutral' and classification = 'Negative' group by [date]""")
    objects_list13 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list13.append(d)
    objects_list[1]["SOS_Neg-Neu_Neg"]=objects_list13
    
    
    
    """Shift Of Sentiment and Negative - Positive"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Negative - Positive'  group by category""")
    objects_list3 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list3.append(d)
    objects_list[2]["Calls_by_Category"]=objects_list3

    """Shift Of Sentiment and Negative - Positive and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Positive' and classification = 'Positive' group by [date]""")
    objects_list14 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list14.append(d)
    objects_list[2]["SOS_Neg-Pos_Pos"]=objects_list14
    
    """Shift Of Sentiment and Negative - Positive and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Negative - Positive' and classification = 'Negative' group by [date]""")
    objects_list15 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list15.append(d)
    objects_list[2]["SOS_Neg-Pos_Neg"]=objects_list15

    
    
    """Shift Of Sentiment and Neutral - Negative"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Neutral - Negative'  group by category""")
    objects_list4 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list4.append(d)
    objects_list[3]["Calls_by_Category"]=objects_list4
    
    """Shift Of Sentiment and Neutral - Negative and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Negative' and classification = 'Positive' group by [date]""")
    objects_list16 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list16.append(d)
    objects_list[4]["SOS_Neu-Neg_Pos"]=objects_list16
    
    """Shift Of Sentiment and Neutral - Negative and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Negative' and classification = 'Negative' group by [date]""")
    objects_list17 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list17.append(d)
    objects_list[4]["SOS_Neu-Neg_Neg"]=objects_list17   
    
    
    """Shift Of Sentiment and Neutral - Neutral"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Neutral - Neutral'  group by category""")
    objects_list5 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list5.append(d)
    objects_list[4]["Calls_by_Category"]=objects_list5
    
    """Shift Of Sentiment and Neutral - Neutral and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Neutral' and classification = 'Positive' group by [date]""")
    objects_list18 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list18.append(d)
    objects_list[5]["SOS_Neu-Neu_Pos"]=objects_list18
    
    """Shift Of Sentiment and Neutral - Neutral and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Neutral' and classification = 'Negative' group by [date]""")
    objects_list19 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list19.append(d)
    objects_list[5]["SOS_Neu-Neu_Neg"]=objects_list19   
    
    """Shift Of Sentiment and Neutral - Positive"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Neutral - Positive'  group by category""")
    objects_list6 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list6.append(d)
    objects_list[5]["Calls_by_Category"]=objects_list6
    
    """Shift Of Sentiment and Neutral - Positive and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Positive' and classification = 'Positive' group by [date]""")
    objects_list20 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list20.append(d)
    objects_list[5]["SOS_Neu-Pos_Pos"]=objects_list20
    
    """Shift Of Sentiment and Neutral - Positive and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Neutral - Positive' and classification = 'Negative' group by [date]""")
    objects_list21 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list21.append(d)
    objects_list[5]["SOS_Neu-Pos_Neg"]=objects_list21
    
    
    """Shift Of Sentiment and Positive - Negative"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Positive - Negative'  group by category""")
    objects_list7 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list7.append(d)
    objects_list[6]["Calls_by_Category"]=objects_list7
    
    """Shift Of Sentiment and Positive - Negative and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Negative' and classification = 'Positive' group by [date]""")
    objects_list22 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list22.append(d)
    objects_list[6]["SOS_Pos-Neg_Pos"]=objects_list22
    
    """Shift Of Sentiment and Positive - Negative and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Negative' and classification = 'Negative' group by [date]""")
    objects_list23 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list23.append(d)
    objects_list[6]["SOS_Pos-Neg_Neg"]=objects_list23
    
    """Shift Of Sentiment and Positive - Neutral"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Positive - Neutral'  group by category""")
    objects_list8 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list8.append(d)
    objects_list[7]["Calls_by_Category"]=objects_list8   

    """Shift Of Sentiment and Positive - Neutral and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Neutral' and classification = 'Positive' group by [date]""")
    objects_list24 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list24.append(d)
    objects_list[7]["SOS_Pos-Neu_Pos"]=objects_list24
    
    """Shift Of Sentiment and Positive - Negative and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Neutral' and classification = 'Negative' group by [date]""")
    objects_list25 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list25.append(d)
    objects_list[7]["SOS_Pos-Neu_Neg"]=objects_list25
    
    
    """Shift Of Sentiment and Positive - Positive"""
    cursor.execute("""Select count(Id) Total_Categories, category as Call_Category from [tblCalls] 
                        where shift_of_sentiment = 'Positive - Positive'  group by category""")
    objects_list9 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Call_Category'] = row.Call_Category
        d['Total_Categories'] = row.Total_Categories
        objects_list9.append(d)
    objects_list[8]["Calls_by_Category"]=objects_list9 
    
    """Shift Of Sentiment and Positive - Positive and Positive Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Positive' and classification = 'Positive' group by [date]""")
    objects_list26 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list26.append(d)
    objects_list[8]["SOS_Pos-Pos_Pos"]=objects_list26
    
    """Shift Of Sentiment and Positive - Positive and Negative Sentiment"""
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                       shift_of_sentiment = 'Positive - Positive' and classification = 'Negative' group by [date]""")
    objects_list27 = []
    for row in cursor.fetchall():
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list27.append(d)
    objects_list[8]["SOS_Pos-Pos_Neg"]=objects_list27
        
    output_dictionary["Shift_of_Sentiments"]=objects_list 
    
    Output_Json = json.dumps(output_dictionary)
    return Output_Json
    

@app.route('/api/page1_agent_filter', defaults={'agent_id':'tblcalls.agent_id'})
@app.route('/api/page1_agent_filter/<int:agent_id>',methods = ['GET'])
def agents_info(agent_id):
    output_dictionary = {}
    
    """Agent Data"""
    cursor.execute("""select 
						tblcalls.agent_id as Agent_Id,
                    	emp.[f-name] as Agent_Name,						
						(count(category)* 100.0 / (Select Count(category) From [tblCalls])) as Calls_Within_180secs,
                    	avg(sentiment_score) as Sentiment_Score ,
                    	avg(duration) as Average_Call_Duration ,
                    	count(category) as Total_Calls ,
                    	sum(case when classification = 'Neutral' then 1 else 0 end) as Neutral_Calls,
                    	sum(case when classification = 'Negative' then 1 else 0 end) as Negative_Calls,
                    	sum(case when classification = 'Positive' then 1 else 0 end) as Positive_Calls,
                    	sum(case when is_explicit = '1' then 1 else 0 end) as Explicit_Calls_Count
                    from 
                    	tblcalls 
                    	Right join  emp 
                    		on tblcalls.agent_id = emp.agent_id 
                            where tblcalls.agent_id = """+str(agent_id)+"""
                    group by emp.[f-name],tblcalls.agent_id """)  
    
    rows = cursor.fetchall() 
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Agent_Id'] = row.Agent_Id
        d['Agent_Name'] = row.Agent_Name
        d['Calls_Within_180secs'] = float(row.Calls_Within_180secs)
        d['Sentiment_Score'] = row.Sentiment_Score
        d['Average_Call_Duration'] = row.Average_Call_Duration
        d['Total_Calls'] = row.Total_Calls
        d['Neutral_Calls'] = row.Neutral_Calls
        d['Negative_Calls'] = row.Negative_Calls
        d['Positive_Calls'] = row.Positive_Calls
        d['Explicit_Calls_Count'] = row.Explicit_Calls_Count
        objects_list.append(d)    
    output_dictionary["Agent_Data"]=objects_list
    
    Output_Json = json.dumps(output_dictionary)
    return Output_Json

@app.route('/api/page2_agent_filter', defaults={'agent_id':'tblcalls.agent_id'})
@app.route('/api/page2_agent_filter/<int:agent_id>', methods = ['GET'])
def agent_filter(agent_id):
    output_dictionary = {}
    
    cursor.execute("""select 
                    		tblcalls.agent_id as Agent_Id,
                            emp.[f-name] as Agent_Name,
                    		tblcalls.category as Category,
                    		Count(category) as Total_Categories,
                            tblcalls.call_category as Call_Category,
		                    Count(category) as Total_Call_Categories,
                    		tblcalls.shift_of_sentiment as Shift_of_Sentiment,
                    		Count(category) as Total_Sentiments
                        	from 
                            tblcalls 
                            Right join  emp 
                                on tblcalls.agent_id = emp.agent_id 
                                where tblcalls.agent_id = """+str(agent_id)+"""
                        	group by emp.[f-name],tblcalls.agent_id,tblcalls.category,tblcalls.call_category,
                            tblcalls.shift_of_sentiment""")
    
    rows = cursor.fetchall() 
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Agent_Id'] = row.Agent_Id
        d['Agent_Name'] = row.Agent_Name
        d['Category'] = row.Category
        d['Total_Categories'] = row.Total_Categories
        d['Call_Category'] = row.Call_Category
        d['Total_Call_Categories'] = row.Total_Call_Categories
        d['Shift_of_Sentiment'] = row.Shift_of_Sentiment
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list.append(d)
        
    output_dictionary["Agent_Data"]=objects_list
    
    Output_Json = json.dumps(output_dictionary)
    return Output_Json

@app.route('/api/page2_bar_chart', methods = ['GET'])
def bar_chart():
    output_dictionary = {}
    
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                        classification = 'Positive' group by [date]""")
    rows = cursor.fetchall() 
    objects_list1 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list1.append(d)
        
    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Tuesday' group by category""")        
    rows = cursor.fetchall() 
    objects_list2 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list2.append(d) 
    objects_list1[0]["Categories"]=objects_list2 
    
    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Tuesday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list9 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list9.append(d) 
    objects_list1[0]["shift_of_sentiment"]=objects_list9

    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Wednesday' group by category""")        
    rows = cursor.fetchall() 
    objects_list3 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list3.append(d) 
    objects_list1[1]["Categories"]=objects_list3
    
    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Wednesday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list10 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list10.append(d) 
    objects_list1[1]["shift_of_sentiment"]=objects_list10

    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Saturday' group by category""")        
    rows = cursor.fetchall() 
    objects_list4 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list4.append(d) 
    objects_list1[2]["Categories"]=objects_list4                  
     
    output_dictionary["Positive_Sentiments"]=objects_list1
    
    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Positive' and DATENAME(WEEKDAY,[date]) = 'Saturday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list11 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list11.append(d) 
    objects_list1[2]["shift_of_sentiment"]=objects_list11
    
    cursor.execute("""select count(Id) Total_Sentiments, DATENAME(WEEKDAY,[date]) as Day_of_Week from [tblCalls] where 
                        classification = 'Negative' group by [date]""")
    rows = cursor.fetchall() 
    objects_list5 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Day_of_Week'] = row.Day_of_Week
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list5.append(d)
        
    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Tuesday' group by category""")        
    rows = cursor.fetchall() 
    objects_list6 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list6.append(d) 
    objects_list5[0]["Categories"]=objects_list6 
    
    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Tuesday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list12 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list12.append(d) 
    objects_list5[0]["shift_of_sentiment"]=objects_list12

    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Thursday' group by category""")        
    rows = cursor.fetchall() 
    objects_list7 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list7.append(d) 
    objects_list5[1]["Categories"]=objects_list7
    
    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Thursday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list13 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list13.append(d) 
    objects_list5[1]["shift_of_sentiment"]=objects_list13

    cursor.execute("""select count(Id) Total_Sentiments, category as Category from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Friday' group by category""")        
    rows = cursor.fetchall() 
    objects_list8 = []
    for row in rows:
        d = collections.OrderedDict()
        d['Category'] = row.Category
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list8.append(d) 
    objects_list5[2]["Categories"]=objects_list8 

    cursor.execute("""select count(Id) Total_Sentiments, shift_of_sentiment as SOS from [tblCalls] where 
                        classification = 'Negative' and DATENAME(WEEKDAY,[date]) = 'Friday' group by shift_of_sentiment""")        
    rows = cursor.fetchall() 
    objects_list14 = []
    for row in rows:
        d = collections.OrderedDict()
        d['SOS'] = row.SOS
        d['Total_Sentiments'] = row.Total_Sentiments
        objects_list14.append(d) 
    objects_list5[2]["shift_of_sentiment"]=objects_list14         
        
    output_dictionary["Negative_Sentiments"]=objects_list5


    Output_Json = json.dumps(output_dictionary)
    return Output_Json


@app.route('/api/joined', methods = ['GET'])
def joined_data():
    output_dictionary = {}
    
    cursor.execute("""select
                    		[f-name] as Agent_Name,
                    		tblcalls.agent_id as Agent_Id,
                    		f_name,
                    		transcription,
                    		intent,
                    		explicitwords,
                    		is_explicit,
                    		keywords,
                    		sentiment_score,category,classification,mobile_no,[date] as Dates, [time] as Time_,
                    		shift_of_sentiment,duration,call_category,survey_about,created_at,initiated_by
                    	from
                    		emp right join tblcalls on tblcalls.agent_id = emp.agent_id""")        
    rows = cursor.fetchall() 
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Agent_Id'] = row.Agent_Id
        d['Agent_Name'] = row.Agent_Name
        d['Audio_file'] = row.f_name
        d['Transcription'] = row.transcription
        d['Intent'] = row.intent
        d['explicitwords'] = row.explicitwords
        d['is_explicit'] = row.is_explicit
        d['Keywords'] = row.keywords
        d['Sentiment_score'] = row.sentiment_score
        d['Category'] = row.category
        d['Classification'] = row.classification
        d['mobile_no'] = row.mobile_no
        d['Date'] = str(row.Dates)
        d['Time'] = str(row.Time_)
        d['shift_of_sentiment'] = row.shift_of_sentiment
        d['Duration'] = row.duration
        d['Call_category'] = row.call_category
        d['survey_about'] = row.survey_about
        d['created_at'] = str(row.created_at)
        d['initiated_by'] = row.initiated_by
        objects_list.append(d)         
    output_dictionary["All_Records"]=objects_list

    Output_Json = json.dumps(output_dictionary)
    return Output_Json

if __name__ == '__main__':
    app.debug = False
    app.run(host = '192.168.100.122')  #put your ip address to host locally









