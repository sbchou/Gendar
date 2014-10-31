import twitter
import json
import sexmachine.detector as gender
from genderize import Genderize
from hammock import Hammock as GendreAPI
import string

""" 
Test various gender libraries on training, data!
"""
# Initialize all yo shit
CONSUMER_KEY = "RE9RJs5c3zQ8yhLCZQCKlVglT"
CONSUMER_SECRET = "iA5ElxRl9JWm4wYDntSI2UxT56Yp6SpcDkAJ40EoDvMMFnWkfK"
ACCESS_TOKEN = "359150678-DAyroyYOpYkqLiCaNIok2M9KoY2fj1C4fxBO5v6R"
ACCESS_TOKEN_SECRET= "zhTmAekrR0hcX4yfV4mRLVx1OQZMuIikj3dTvtfzghjAZ"

api = twitter.Api(consumer_key = CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
sexmachine = gender.Detector()
gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")

def process(user_ids):
    pass

def infer_sex(data_path, output_path, n=100):
    data = json.load(open(data_path, 'r'))
    output = open(output_path, 'w')

    ids = data.keys()
    twps = api.UsersLookup(user_id=ids[:n])

    output.write("name\tlocation\tgender_gold\tgender_sexmachine\tgender_genderize\tgender_gendre\tavg_score\n")
    for t in twps:
        screen_name = t.screen_name
        name = t.name
        location = t.location if t.location else "None"

        # WE SPEAK AMERICAN HERE
        cleanedname = filter(lambda x: x in string.printable, name).strip()   
        if cleanedname:
            splitname = cleanedname.split()
            firstname = splitname[0]
            lastname = splitname[-1] if len(splitname) > 1 else None
            gender_gold = data[str(t.id)]
            gender_sexmachine = sexmachine.get_gender(firstname)
            if gender_sexmachine == "male":
                sexmachine_score = -1;
            if gender_sexmachine == "female": 
                sexmachine_score = 1;
            if gender_sexmachine == "andy":
                sexmachine_score = 0;
            if gender_sexmachine == "mostly_female":
                sexmachine_score = 0.5;
            if gender_sexmachine == "mostly_male":
                sexmachine_score = -0.5;

            gender_genderize = Genderize().get([firstname])[0]['gender']
            genderize_prob = Genderize().get([firstname])[0]['probability']
            if gender_genderize == "male":
                genderize_score = -1 * genderize_prob
            else:
                genderize_score = genderize_prob

            resp = gendre(firstname, lastname).GET() # also add country code?
            gender_gendre = resp.json().get('gender')
            # Scale -1 being M to +1 being F
            gendre_score = resp.json().get('scale')

            avg_score = (sexmachine_score + genderize_score + gendre_score) / 3.0
            import pdb; pdb.set_trace()            
            values = [name, location, gender_gold, gender_sexmachine, \
                    gender_genderize, gender_gendre, str(avg_score)]
    
            values = [v.encode('ascii', 'ignore') if v is not None else "None" for v in values]

            #print gender_sexmachine, type(gender_sexmachine), gender_genderize, type(gender_genderize), gender_gendre, type(gender_gendre)
            output.write("\t".join(values) + "\n")

    output.close()

infer_sex('data/labels.json', 'data/output.tsv', 50)

