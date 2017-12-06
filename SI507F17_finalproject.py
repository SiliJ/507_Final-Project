import webbrowser
import json
import config
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

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
unique_ident = params_unique_combination(foodfinder_url,inquiry_param)
if unique_ident in CACHE_DICTION:
    print("Getting cached data...")
    print(CACHE_DICTION[unique_ident])
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
    print ('add inquiry term')
