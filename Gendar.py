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
    clf = svm.SVC()
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

