print "Content-type: text/html\n\n"

import json
import urllib2
import sys
sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")
from elasticsearch import Elasticsearch
import glob
import fnmatch
import os
import sys
from marvinTestResultsHtml import *
from startElastic import indexLogs
#from startElastic import sendQuery
import pdb
pdb.set_trace()
logsDir = "/var/www/LogAnalyzer/results"
st_time = "Sat Apr 12 03:40:23 2014"
end_time = "Sat Apr 12 03:41:33 2014"
query = {
    "size" : 100000,
    "query": {
            "bool": {
                    "must" :[
                            {"wildcard" : {"file" : "*" }},
                            {"wildcard" : {"level" : "*" }},
                            {"range": {"time" : {"gte":st_time , "lte":end_time}}}
                            ]
                    }
            }
            }
es = indexLogs(logsDir)
#res = sendQuery("Sat Apr 12 03:40:23 2014", "Sat Apr 12 03:41:33 2014")
res = es.search(index="test", body={"query": {"bool": {"must": {"wildcard": {"file": "*"}}}}})
print res
