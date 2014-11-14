import twitter
import json
import sexmachine.detector as gender
from genderize import Genderize
from hammock import Hammock as GendreAPI
import string
import psycopg2
import sys
import pandas

"""
Test various gender libraries on training, data!
"""
def svm():
    # must convert label index to string
    features.index = features.index.astype('int64')
    labeled = features.join(labels)
    labeled = labeled.as_matrix()
    labeled = labeled[np.isfinite(labeled['sex'])]
    from sklearn import svm
    clf = svm.SVC
    mtx = labeled.as_matrix()
    X = mtx[:, 0:3]
    Y = mtx[:,4]
    X_train = X[0:10000,;]
    Y_train = Y[0:10000]
    clf.fit(X_train, Y_train)
    pred = clf.predict(X[10000:len(X)])
    sum(1.0 * (pred == Y[10000:])) / len(Y[10000:]) #64%

def compute_profile_features(data):
    """ Compute features for classification"""
    motherwords = ["mom", "mother", "mommy", "mama"]
    fatherwords = ["dad", "father", "daddy", "papa"]
   
    # Find if there are motherwords 
    motherwords = data.apply(lambda row: any(word in row['description'].split() \
                for word in motherwords) \
                if pandas.notnull(row['description']) \
                else False, \
                1)
        
    # Find if there are fatherwords
    fatherwords = data.apply(lambda row: any(word in row['description'].split() \
                for word in fatherwords) \
                if pandas.notnull(row['description']) \
                else False, \
                1)

    data['motherwords'] = motherwords * 1
    data['fatherwords'] = fatherwords * 1

   # some gay stuff
   lwords = data.apply(lambda row: "lesbian" in row['description'] \
                if pandas.notnull(row['description']) \
                else False, \
                1)
    
    data["lwords"] = lwords * 1

 
def compute_name_features(data):
        firstname = data.apply(lambda row: row['cleanedname'].split()[0] \
            if pandas.notnull(row['cleanedname']) \
            else None, 1)
        
        lastname = data.apply(lambda row: row['cleanedname'].split()[-1] \
            if pandas.notnull(row['cleanedname']) \
            and len(row['cleanedname'].split()) > 1 \
            else None, 1)
        
        data['firstname'] = firstname
        data['lastname'] = lastname

        gendre = data.apply(get_gendre, 1) 
        data['gendre'] = gendre

def get_gendre(row):
    gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")
    firstname = row['firstname']
    lastname = row['lastname']
    if firstname:
        try:
            resp = gendre(firstname, lastname).GET() 
            score = resp.json().get('scale')
            return score
        except:
            "error"
        else: 
            return None
    return None

def play():
    labels = pandas.read_csv('data/labels.tsv', sep="\t", index_col=0)
    data = pandas.read_csv('data/gold.tsv', sep="\t", index_col=0)
    data = data.drop('Unnamed: 7',1)
    l = list(labels.index)
    l = [str(x) for x in l]
    labels.index = l
    joined = data.join(labels)

    f_bios = joined[joined.sex=="F"].description
    f_bios = f_bios[f_bios.notnull()]

    m_bios = joined[joined.sex=="M"].description
    m_bios = m_bios[m_bios.notnull()]

    motherwords = ["mom", "mommy", "mother", "children"]
    fatherwords = ["dad", "daddy", "father", "children"]

    print "motherwords"
    num_mom = len([f for f in f_bios if any(x in f for x in motherwords)])
    print num_mom, num_mom / (1.0 * len(f_bios)) # 0.0193

    print "fatherwords"
    num_dad = len([m for m in m_bios if any(x in m for x in fatherwords)])
    print num_dad, num_dad / (1.0 * len(m_bios)) # 0.0139

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
        in_path = args[2]
        out_path = args[3]
        get_gold(in_path, out_path)
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
    gendre = gendreapi("http://api.namsor.com/onomastics/api/json/gendre")

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

