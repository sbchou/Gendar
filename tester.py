""" 
Test various gender libraries on training, testing!
"""
import twitter
import json

CONSUMER_KEY = "RE9RJs5c3zQ8yhLCZQCKlVglT"
CONSUMER_SECRET = "iA5ElxRl9JWm4wYDntSI2UxT56Yp6SpcDkAJ40EoDvMMFnWkfK"
ACCESS_TOKEN = "359150678-DAyroyYOpYkqLiCaNIok2M9KoY2fj1C4fxBO5v6R"
ACCESS_TOKEN_SECRET= "zhTmAekrR0hcX4yfV4mRLVx1OQZMuIikj3dTvtfzghjAZ"

api = twitter.Api(consumer_key = CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

testing = json.load(open('data/labels.json', 'r'))
ids = testing.keys()

# We that are rate-limited
n = 200
twps = api.UsersLookup(user_id=ids[:100])

for t in twps:
    screen_name = t.screen_name
    name = t.name
    location = t.location
    gender_gold = testing[str(t.id)]
  
    print name, location, gender_gold

