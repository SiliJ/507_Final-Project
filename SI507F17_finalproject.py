import webbrowser
import json
import config
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import psycopg2
import sys
import psycopg2.extras
import csv
import os.path
# from flask import Flask, request, render_template

# setting up basic info
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True    #(what's the use fo this? How shall we use)
CACHE_FNAME = "cache_contents.json"
APP_ID = config.Client_ID
APP_SECRET = config.Client_Secret
TOKEN_URL = 'https://api.yelp.com/oauth2/token'
session = None
searchterm=input('Please type the food you are searching?')
yourplace=input('Please type your location')
foodfinder_url="https://api.yelp.com/v3/businesses/search"
operation_hours_url="https://api.yelp.com/v3/businesses/{id}"

try:
    conn = psycopg2.connect("dbname='foodieguide' user='anita'")
    print ("successful connecting to the server")
except:
    print("Unable to connect to the database. Check server and credentials.")
    sys.exit(1)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("DROP TABLE IF EXISTS operation_hours")
cur.execute("DROP TABLE IF EXISTS restaurant_list")
cur.execute("CREATE TABLE IF NOT EXISTS restaurant_list(ID SERIAL Primary KEY,Name Text UNIQUE, RESTAURANT_ID Text UNIQUE,Rating Real,Review_count INTEGER,Distance REAL,Phone Text,Address Text,Category VARCHAR(80),Transactions VARCHAR(80),Price_range VARCHAR(40))")
# cur.execute("CREATE TABLE IF NOT EXISTS operation_hours(restaurant_id Text references restaurant_list(ID), Monday Text,Tuesday Text,Wednesday Text,Thursday Text,Friday Text,Saturday Text, Sunday Text)")
cur.execute("CREATE TABLE IF NOT EXISTS operation_hours(ID SERIAL Primary KEY, store_ID Text references restaurant_list(RESTAURANT_ID), Weekday VARCHAR NOT NULL,start_at integer,end_at integer)")



# setting up CATCHING System
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params_d, private_keys=["APP_ID"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

def make_request(url, params=None):
    global session
    if not session:
        start_session()
    if not params:
        params = {}
    return session.get(url, params=params)

def start_session():
    global session
    # 0 - get token from cache
    try:
        token = get_saved_token()
    except FileNotFoundError:
        token = None
    if token:
        session = OAuth2Session(APP_ID, token=token)
    else:
        # 1 - session
        client = BackendApplicationClient(client_id=APP_ID)
        session = OAuth2Session(client=client)
        # 2 - token
        token = session.fetch_token(token_url=TOKEN_URL, client_id=APP_ID, client_secret=APP_SECRET)
        # 3 - save token
        save_token(token)

def get_saved_token():
    with open('token.json', 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)
        return token_dict

def save_token(token_dict):
    with open('token.json', 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)

inquiry_param={}
inquiry_param['term']=searchterm
inquiry_param['location']=yourplace
inquiry_param['limit']=50
unique_ident = params_unique_combination(foodfinder_url,inquiry_param)
if unique_ident in CACHE_DICTION:
    print("Getting cached data...")
    # print(CACHE_DICTION[unique_ident])
else:
    print("Making a request for new data...")
    r = make_request('https://api.yelp.com/v3/businesses/search', inquiry_param)
    # print(r.text)
    CACHE_DICTION[unique_ident]=json.loads(r.text)
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close() # Close the open file
    print(unique_ident)
    # return CACHE_DICTION[unique_ident]
    # print ('add inquiry term')

class Restaurant(object):
        # restaurant data
        def __init__(self, item):
            self.ID=item['id']
            self.name=item['name']
            self.rating=item['rating']
            self.review_count=item['review_count']
            self.distance=item['distance']
            self.phone=item['phone']
            self.address=item['location']['address1']+" "+item['location']['city']
            categorylist=[]
            for elem in item['categories']:
                type=elem['title']
                categorylist.append(type)
            self.category=categorylist
            services=[]
            for elem in item['transactions']:
                service_type=elem
                services.append(service_type)
            self.transactions=services
            self.price_range=item['price']
        # get resaturant data into dictionary
        def get_restaurant_dict(self):
            return {
                'id': self.ID,
                'name': self.name,
                'rating': self.rating,
                'review_count': self.review_count,
                'distance': self.distance,
                'phone': self.phone,
                'address': self.address,
                'category': self.category,
                'transactions': self.transactions,
                'price_range':self.price_range
            }
        def get_restaurant_id(self):
            return self.ID
        def get_operation_hours(self):
            ID=self.ID
            hoursURL="https://api.yelp.com/v3/businesses/"+ID
            hours_param={}
            hours_param={}
            hours_param['locale']='en_US'
            r2=make_request(hoursURL,hours_param)
            CACHE_DICTION[ID]=json.loads(r2.text)
            dumped_json_cache = json.dumps(CACHE_DICTION)
            fw = open(CACHE_FNAME,"w")
            fw.write(dumped_json_cache)
            fw.close() # Close the open file
            return CACHE_DICTION[ID]

        def __repr__(self):
            return "your search for relevant restaurant_list is: {}".format(self.ID)

        def __contains__(self,x):
            return x in self.category

# class hours(obect):

def insert_restaurant_data(restaurant_data,conn,cur):
    """Inserts restaurant data and returns restaurant_ID, None if unsuccessful"""
    sql = """INSERT INTO restaurant_list(Name,RESTAURANT_ID,Rating,Review_count,Distance,Phone,Address,Category,Transactions,Price_range) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cur.execute(sql,(restaurant_data['name'],restaurant_data['id'],restaurant_data['rating'],restaurant_data['review_count'],restaurant_data['distance'],restaurant_data['phone'],restaurant_data['address'],restaurant_data['category'],restaurant_data['transactions'],restaurant_data['price_range']))
    conn.commit()
    # print('restaurant_data inserted')
    return True

def insert_hours_data(store_ID,Weekday,start,end,conn,cur):
    """Inserts restaurant operation hours, None if unsuccessful"""
    sql = """INSERT INTO operation_hours(store_ID,Weekday,start_at,end_at) VALUES(%s,%s,%s,%s)"""
    cur.execute(sql,(store_ID,Weekday,start,end))
    conn.commit()
    return True

# Invoke class fuction to get restaurant data and finish data insertation for restaurants
business_list=CACHE_DICTION[unique_ident]['businesses']
operation_time_result=[]
restaurantfile=open("restaurants.csv","w")
restaurantfile.write("Name,Rating,Review Number,distance,phone,address,category,transactions,price_range\n")
for item in business_list:
    Restaurants_object=Restaurant(item)
    Restaurants_data=Restaurants_object.get_restaurant_dict()
    # print(Restaurants_data)
    # ID=Restaurants_data['id']
    insert_restaurant_data(Restaurants_data,conn,cur)
    # print("restaurant data inserted well")
    restaurantfile.write("{},{},{},{},{},{},{},{},{}\n".format(Restaurants_data['name'],Restaurants_data['rating'],Restaurants_data['review_count'],Restaurants_data['distance'],Restaurants_data['phone'],Restaurants_data['address'],Restaurants_data['category'],Restaurants_data['transactions'],Restaurants_data['price_range']))

    #use orangisation ID to get its operation hours
    ID=Restaurants_data['id']
    # # print(ID)
    hours_object=Restaurants_object.get_operation_hours()
    ID_openinginfo=hours_object['hours'][0]['open']
    # operation_time={}
    # # operation_time['Mon']=[]
    # # operation_time['Tue']=[]
    # # operation_time['Wed']=[]
    # # operation_time['Thu']=[]
    # # operation_time['Fri']=[]
    # # operation_time['Sat']=[]
    # # operation_time['Sun']=[]
    # # timetable=[]
    # # restaruant_hours={}
    for time in ID_openinginfo:
        if time['day']==1:
            Weekday="Monday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)
            # timetable.append(operation_time['Monday'])

        if time['day']==2:
            Weekday="Tuesday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)

        if time['day']==3:
            Weekday="Wednesday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)


        if time['day']==4:
            Weekday="Thursday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)

        if time['day']==5:
            Weekday="Friday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)

        #
        if time['day']==6:
            Weekday="Saturday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)
        #
        if time['day']==0:
            Weekday="Sunday"
            start=time['start']
            end=time['end']
            opearationhrs_database=insert_hours_data(ID,Weekday,start,end,conn,cur)

restaurantfile.close()

instruction=input('which restaurant do you like?')
# searchtuple=(instruction)
# cur.execute("SELECT RESTAURANT_ID FROM restaurant_list where name=%s",(instruction,))
# selectedID=cur.fetchall()
# print(selectedID)
cur.execute("SELECT Weekday, start_at, end_at FROM operation_hours INNER JOIN restaurant_list ON operation_hours.store_ID=restaurant_list.RESTAURANT_ID WHERE restaurant_list.name=%s",(instruction,))
timetable=cur.fetchall()
# timetable=cur.fetchall()
# print(timetable)
            # operation_time['Sun'].append(time['start']+"-"+time['end'])
    # restaruant_hours[ID]=operation_time


    # operation_time_result.append(restaruant_hours)
    # opearationhrs_database=insert_hours_data(conn,cur)

# print(operation_time_result)
# print('operation_time inserted into database')
    # ID=Restaurants_object.get_restaurant_id()
#     hoursURL="https://api.yelp.com/v3/businesses/"+ID
#     hours_param={}
#     hours_param['locale']='en_US'
#     r2=make_request(hoursURL,hours_param)
#     # print(r2.text)
#     CACHE_DICTION[ID]=json.loads(r2.text)
# #     # print (CACHE_DICTION[ID])
#     dumped_json_cache = json.dumps(CACHE_DICTION)
#     fw = open(CACHE_FNAME,"w")
#     fw.write(dumped_json_cache)
#     fw.close() # Close the open file
# print('restaurant_data inserted')
# print('operationhours downloaded')

#organizing hours data and insert them into base
    # ID_openinginfo=CACHE_DICTION[ID]['hours'][0]['open']
    # operation_time={}
    # restaruant_hours={}
    # operation_time['Mon']=[]
    # operation_time['Tue']=[]
    # operation_time['Wed']=[]
    # operation_time['Thu']=[]
    # operation_time['Fri']=[]
    # operation_time['Sat']=[]
    # operation_time['Sun']=[]
    # for time in ID_openinginfo:
    #     if time['day']==1:
    #         operation_time['Mon'].append(time['start']+"-"+time['end'])
    #     if time['day']==2:
    #         operation_time['Tue'].append(time['start']+"-"+time['end'])
    #     if time['day']==3:
    #         operation_time['Wed'].append(time['start']+"-"+time['end'])
    #     if time['day']==4:
    #         operation_time['Thu'].append(time['start']+"-"+time['end'])
    #     if time['day']==5:
    #         operation_time['Fri'].append(time['start']+"-"+time['end'])
    #     if time['day']==6:
    #         operation_time['Sat'].append(time['start']+"-"+time['end'])
    #     if time['day']==0:
    #         operation_time['Sun'].append(time['start']+"-"+time['end'])
#         restaruant_hours[ID]=operation_time
#         operation_time_result.append(restaruant_hours)
# #     # print (operation_time_result)
#         opearationhrs_database=insert_hours_data(ID,operation_time['Mon'],operation_time['Tue'],operation_time['Wed'],operation_time['Thu'],operation_time['Fri'],operation_time['Sat'],operation_time['Sun'],conn,cur)
#
# print ('operation hour data inserted')
#     operation_time={}
#     restaruant_hours={}
#     operation_time['Sunday']=[]
#     operation_time['Monday']=[]
#     operation_time['Tuesday']=[]
#     operation_time['Wednesday']=[]
#     operation_time['Thursday']=[]
#     operation_time['Friday']=[]
#     operation_time['Saturday']=[]
#     for time in ID_openinginfo:
#         if time['day']==1:
#             operation_time['Monday'].append(time['start']+"-"+time['end'])
#         if time['day']==2:
#             operation_time['Tuesday'].append(time['start']+"-"+time['end'])
#         if time['day']==3:
#             operation_time['Wednesday'].append(time['start']+"-"+time['end'])
#         if time['day']==4:
#             operation_time['Thursday'].append(time['start']+"-"+time['end'])
#         if time['day']==5:
#             operation_time['Friday'].append(time['start']+"-"+time['end'])
#         if time['day']==6:
#             operation_time['Saturday'].append(time['start']+"-"+time['end'])
#         if time['day']==0:
#             operation_time['Sunday'].append(time['start']+"-"+time['end'])
#     restaruant_hours[ID]=operation_time
#     operation_time_result.append(restaruant_hours)
# print (operation_time_result)
# print('updated cache_file with each restaurant's operation_hours')

#     restaruant_hours={}
#     ID_hoursinfo=CACHE_DICTION[ID]['hours'][0]['open']
#     operation_time={}
#     operation_time['Sunday']=[]
#     operation_time['Monday']=[]
#     operation_time['Tuesday']=[]
#     operation_time['Wednesday']=[]
#     operation_time['Thursday']=[]
#     operation_time['Friday']=[]
#     operation_time['Saturday']=[]
#     for time in ID_hoursinfo:
#         if time['day']==1:
#             operation_time['Monday'].append(time['start']+"-"+time['end'])
#         if time['day']==2:
#             operation_time['Tuesday'].append(time['start']+"-"+time['end'])
#         if time['day']==3:
#             operation_time['Wednesday'].append(time['start']+"-"+time['end'])
#         if time['day']==4:
#             operation_time['Thursday'].append(time['start']+"-"+time['end'])
#         if time['day']==5:
#             operation_time['Friday'].append(time['start']+"-"+time['end'])
#         if time['day']==6:
#             operation_time['Saturday'].append(time['start']+"-"+time['end'])
#         if time['day']==0:
#             operation_time['Sunday'].append(time['start']+"-"+time['end'])
#         restaruant_hours[ID]=operation_time
#         Sum_storehours.append(restaruant_hours)
# print (Sum_storehours)
# print('updated cache_file with each restaurant's operation_hours')



# searchresult=[]
# operation_time_result=[]
# # business_list=CACHE_DICTION[unique_ident]['businesses']
# for item in business_list:
#     restaurant={}
#     restaurant['ID']=item['id']
#     restaurant['name']=item['name']
#     restaurant['rating']=item['rating']
#     restaurant['review_count']=item['review_count']
#     restaurant['distance']=item['distance']
#     restaurant['phone']=item['phone']
#     restaurant['address']=item['location']['address1']+" "+item['location']['city']
#     categorylist=[]
#     for elem in item['categories']:
#         type=elem['title']
#         categorylist.append(type)
#     restaurant['category']=categorylist
#     services=[]
#     for elem in item['transactions']:
#         service_type=elem
#         services.append(service_type)
#     restaurant['transactions']=services
#     restaurant['price_range']=item['price']
#     searchresult.append(restaurant)
#     print (searchresult)
    # print ("your seearch for restaurant_list is ready and is stored in cache_file")
    #setting up another catching api and organizing  operation time for each  restaurant
#     ID=restaurant['ID']
#     hoursURL="https://api.yelp.com/v3/businesses/"+ID
#     hours_param={}
#     hours_param['locale']='en_US'
#     r2=make_request(hoursURL,hours_param)
# # print(r2.text)
#     CACHE_DICTION[ID]=json.loads(r2.text)
#     dumped_json_cache = json.dumps(CACHE_DICTION)
#     fw = open(CACHE_FNAME,"w")
#     fw.write(dumped_json_cache)
#     fw.close() # Close the open file
#     ID_openinginfo=CACHE_DICTION[ID]['hours'][0]['open']
#     operation_time={}
#     restaruant_hours={}
#     operation_time['Sunday']=[]
#     operation_time['Monday']=[]
#     operation_time['Tuesday']=[]
#     operation_time['Wednesday']=[]
#     operation_time['Thursday']=[]
#     operation_time['Friday']=[]
#     operation_time['Saturday']=[]
#     for time in ID_openinginfo:
#         if time['day']==1:
#             operation_time['Monday'].append(time['start']+"-"+time['end'])
#         if time['day']==2:
#             operation_time['Tuesday'].append(time['start']+"-"+time['end'])
#         if time['day']==3:
#             operation_time['Wednesday'].append(time['start']+"-"+time['end'])
#         if time['day']==4:
#             operation_time['Thursday'].append(time['start']+"-"+time['end'])
#         if time['day']==5:
#             operation_time['Friday'].append(time['start']+"-"+time['end'])
#         if time['day']==6:
#             operation_time['Saturday'].append(time['start']+"-"+time['end'])
#         if time['day']==0:
#             operation_time['Sunday'].append(time['start']+"-"+time['end'])
#     restaruant_hours[ID]=operation_time
#     operation_time_result.append(restaruant_hours)
# print (operation_time_result)
# print('updated cache_file with each restaurant's operation_hours')

# Setup connection with database
# try:
#     conn = psycopg2.connect("dbname='foodieguide' user='anita'")
#     print ("successful connecting to the server")
# except:
#     print("Unable to connect to the database. Check server and credentials.")
#     sys.exit(1)
#
# cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# cur.execute("CREATE TABLE IF NOT EXISTS restaurant_list(Auto_ID SERIAL Primary KEY, Name VARCHAR(40) UNIQUE, ID VARCHAR(40) UNIQUE,rating Real,review_count INTEGER,distance REAL,phone Text,address VARCHAR(40),category VARCHAR(40),transactions VARCHAR(40),price_range VARCHAR(40))")
# cur.execute("CREATE TABLE IF NOT EXISTS operation_hours(ID SERIAL Primary KEY,restaurant_ID VARCHAR(40) references restaurant_list(ID), weekday Time,hours VARCHAR(40))")
#
# def insert_restaurant_data(restaurant_data_dict,conn,cur):
#     """Inserts restaurant data and returns restaurant_ID, None if unsuccessful"""
#     sql = """INSERT INTO restaurant_list (Name,ID，rating,review_count,distance,phone,adress,category,transactions,price_range) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ID"""
#     cur.execute(sql,(state_name,))
#     # cur.execute("SELECT * FROM States")
#     # stateID=cur.fetchone()[0]
#     # print(state_name)
#     # print(stateID)
#     # zprint ((ID))
#     #print("State name", State_name)
#     conn.commit()
#     return True
#
# def insert_sites_data(park_name,park_type,state_id,park_location,Description,conn,cur):
#      """Returns True if succcessful, False if not"""
#     #  state_id=insert_states_data(state_name,conn,cur)
#     #  print(state_name)
#      sql = """INSERT INTO Sites(Name,Type,State_ID,Location,Description) VALUES(%s,%s,%s,%s,%s)"""
#      cur.execute(sql,(park_name,park_type,state_id,park_location,Description))
#      conn.commit()
#      return True

 # if __name__ == '__main__':
