import twitter
import json
import sexmachine.detector as gender
from genderize import Genderize
from hammock import Hammock as GendreAPI
import string
import psycopg2
import sys

"""
Test various gender libraries on training, data!
"""

def get_gold(data_path, output_path):
    """Construct the Gold dataset"""
     # Initialize all yo shit
    CONSUMER_KEY = "RE9RJs5c3zQ8yhLCZQCKlVglT"
    CONSUMER_SECRET = "iA5ElxRl9JWm4wYDntSI2UxT56Yp6SpcDkAJ40EoDvMMFnWkfK"
    ACCESS_TOKEN = "359150678-DAyroyYOpYkqLiCaNIok2M9KoY2fj1C4fxBO5v6R"
    ACCESS_TOKEN_SECRET= "zhTmAekrR0hcX4yfV4mRLVx1OQZMuIikj3dTvtfzghjAZ"
    
    api = twitter.Api(consumer_key = CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
     
    data = json.load(open(data_path, 'r'))
    output = open(output_path, 'w')
    output.write("tid\tscreen_name\tname\tcleanedname\tlocation\tdescription\ttime_zone\n")
    ids = data.keys()

    # Do this a chunk at a time to avoid api limit  
    n = len(ids)
    #import pdb; pdb.set_trace()
    for i in xrange(0, n, 100):
        j =  i + 100 if i + 100 <= n else n
        print "Now processing #" + str(i) + " to #" + str(j)
        twps = api.UsersLookup(user_id=ids[i:j])
        for t in twps:
            screen_name = t.screen_name
            name = t.name
            cleanedname = filter(lambda x:x  in string.printable, name).strip()
            location = t.location if t.location else "None"
            description = t.description.strip()
            description = ' '.join(description.split())
            time_zone = t.time_zone
            values = [str(t.id), screen_name, name, cleanedname, location, \
                        description, time_zone]
            values = [v.encode('ascii', 'ignore') if v is not None \
                        else "None" for v in values]             
            output.write("\t".join(values) + "\n")           

    output.close()


def main(args):
    #infer_sex('data/output.tsv')
    #test('data/labels.json', 'data/test_all.tsv')
    if args[1] == "GOLD":
        get_gold('data/labels.json', 'data/gold_clean2.tsv')
    if args[1] == "TEST":
        print "TEST"

if __name__ == "__main__":
    main(sys.argv)


"""

def test(data_path, output_path):
    " No location as of yet"
    # Initialize all yo shit
    CONSUMER_KEY = "RE9RJs5c3zQ8yhLCZQCKlVglT"
    CONSUMER_SECRET = "iA5ElxRl9JWm4wYDntSI2UxT56Yp6SpcDkAJ40EoDvMMFnWkfK"
    ACCESS_TOKEN = "359150678-DAyroyYOpYkqLiCaNIok2M9KoY2fj1C4fxBO5v6R"
    ACCESS_TOKEN_SECRET= "zhTmAekrR0hcX4yfV4mRLVx1OQZMuIikj3dTvtfzghjAZ"
    
    api = twitter.Api(consumer_key = CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
    sexmachine = gender.Detector()
    gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")

    sexmachine = gender.Detector()
    gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")
    
    data = json.load(open(data_path, 'r'))
    output = open(output_path, 'w')
    ids = data.keys()
    twps = api.UsersLookup(user_id=ids[200:300])
   
    print "tid\tscreen_name\tcleanedname\tgender_sexmachine\tgender_genderize\tgender_gendre\tavg_score\tavg_gender\tgender_gold"
    
    for t in twps:
        import pdb; pdb.set_trace()
        screen_name = t.screen_name
        name = t.name
        location = t.location if t.location else "None"

        cleanedname = filter(lambda x:x  in string.printable, name).strip()
        #print str(tid)
        if cleanedname:
            splitname = cleanedname.split()
            firstname = splitname[0]
            lastname = splitname[-1] if len(splitname) > 1 else None
            gender_gold = data[str(t.id)]
            try:
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
                # Sometimes the name will not be in DB and return only gender key,
                # gender = None.
                #if 'probability' not in Genderize().get([firstname])[0].keys():
                #    import pdb; pdb.set_trace()
                if gender_genderize == None:
                    genderize_score = 0.0
                else: 
                    genderize_prob = Genderize().get([firstname])[0]['probability']
                    if gender_genderize == "male":
                        genderize_score = -1 * genderize_prob
                    else:
                        genderize_score = genderize_prob
                #if str(tid) == "61664047":
                #    import pdb; pdb.set_trace()
                resp = gendre(firstname, lastname).GET() # also add country code?
                gender_gendre = resp.json().get('gender')
                # Scale -1 being M to +1 being F
                gendre_score = resp.json().get('scale')

            except:
                print "EXCPETION"
                pass

            else:
                avg_score = (sexmachine_score + genderize_score + gendre_score) / 3.0
                if avg_score > 0.0:
                    avg_gender = "F"
                elif avg_score < 0.0:
                    avg_gender = "M"
                else:
                    avg_gender = "A"

     
                values = [str(t.id), screen_name, cleanedname, gender_sexmachine, \
                        gender_genderize, gender_gendre, str(avg_score), avg_gender, \
                        gender_gold]
     
                values = [v.encode('ascii', 'ignore') if v is not None else "None" for v in values]             
                row = "$$$$$".join(values)     
                print row

def fetch_data(query):
    conn_string = "host='localhost' dbname='cambridge-db' user='cat' password='3GreenSailb0at5'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return records

def infer_sex(output_path):
    "No location as of yet"

    sexmachine = gender.Detector()
    gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")
    
    #output = open(output_path, 'w')
    #output.write("id\tscreen_name\tcleanedname\tgender_sexmachine\tgender_genderize\tgender_gendre\tavg_score\n")
    print "tid\tscreen_name\tcleanedname\tgender_sexmachine\tgender_genderize\tgender_gendre\tavg_score\tavg_gender"
    recs = fetch_data("SELECT id, screen_name, real_name FROM twitter_identity;")
    for r in recs:
        tid, screenname, realname = r
        cleanedname = filter(lambda x:x  in string.printable, realname).strip()
        #print str(tid)
        if cleanedname:
            splitname = cleanedname.split()
            firstname = splitname[0]
            lastname = splitname[-1] if len(splitname) > 1 else None

            try:
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
                # Sometimes the name will not be in DB and return only gender key,
                # gender = None.
                #if 'probability' not in Genderize().get([firstname])[0].keys():
                #    import pdb; pdb.set_trace()
                if gender_genderize == None:
                    genderize_score = 0.0
                else: 
                    genderize_prob = Genderize().get([firstname])[0]['probability']
                    if gender_genderize == "male":
                        genderize_score = -1 * genderize_prob
                    else:
                        genderize_score = genderize_prob
                #if str(tid) == "61664047":
                #    import pdb; pdb.set_trace()
                resp = gendre(firstname, lastname).GET() # also add country code?
                gender_gendre = resp.json().get('gender')
                # Scale -1 being M to +1 being F
                gendre_score = resp.json().get('scale')

            except:
                print "EXcPETION"
                pass

            else:
                avg_score = (sexmachine_score + genderize_score + gendre_score) / 3.0
                if avg_score > 0.0:
                    avg_gender = "F"
                elif avg_score < 0.0:
                    avg_gender = "M"
                else:
                    avg_gender = "A"

     
                values = [str(tid), screenname, cleanedname, gender_sexmachine, \
                        gender_genderize, gender_gendre, str(avg_score), avg_gender]
     
                values = [v.encode('ascii', 'ignore') if v is not None else "None" for v in values]             
                row = "$$$$$".join(values)     
                print row
                #output.write("\t".join(values) + "\n") 
                #output.close()

def infer_sex(data_path, output_path, n):
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
"""

