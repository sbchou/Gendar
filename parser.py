"""
Parse json dumps from Twitter search API
"""

import json

def json_to_tsv(inname, outname):
    text= open(inname, 'r')
    outfile = open(outname, 'w')

    test = json.load(text)
    stats = test['statuses']
    outfile.write("name\tscreen_name\tprofile_location\tdescription")

    for s in stats:
        user = s['user']   
        string = ""
     
        if user['name']:
            string += user['name']
        string += "\t"

        if user['screen_name']:
            string += user['screen_name']
        string += "\t"
        
        if user['profile_location']:
            string += user['profile_location']
        string += "\t"

        if user['description']:
            string += user['description']
        string += "\n"    
        
        outfile.write(string.encode('utf-8'))

    outfile.close()
    
