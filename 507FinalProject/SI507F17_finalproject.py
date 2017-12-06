import requests_oauthlib
import webbrowser
import json
import config
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"
CLIENT_ID = config.Client_ID
CLIENT_SECRET= config.Client_Secret
grant_type='client_credentials'
TOKEN_URL = "https://api.yelp.com/oauth2/token"
REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'

oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
token = oauth2inst.fetch_token(TOKEN_URL, CLIENT_ID, client_secret=CLIENT_SECRET)
print (token)
access_token=token['access_token']
headers{Authorization=access_token,}
searchterm='seafood'
baseurl_storefinder= "https://api.yelp.com/v3/businesses/search?term=delis&latitude=37.786882&longitude=-122.399972"
r=oauth2inst.get(baseurl_storefinder,searchterm)

# AUTHORIZATION_URL = 'https://www.eventbrite.com/oauth/authorize'
# authorization_url, state = oauth2inst.authorization_url(AUTHORIZATION_URL)
# webbrowser.open(authorization_url)
# authorization_response = input('Authenticate and then enter the full callback URL: ').strip()
# r = oauth2inst.get('https://www.eventbriteapi.com/v3/users/me/?token=SESXYS4X3FJ5LHZRWGKQ')
# response_diction = json.loads(r.text)



# searchterm=raw_input("What do you want to have for today")
# location=raw_input("Please change your location setting?")
