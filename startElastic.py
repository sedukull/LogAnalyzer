#!/usr/bin/python2.7 


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

def sendQuery( st_time, end_time ):
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
    url= "http://localhost:9200/test/_search"
    #url= "http://10.147.38.151:9200/test/_search"
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(query))
    return response


#es = Elasticsearch()

def readFile(filename, file, es):
    #global esh
    lines = open(filename, "r")
    count = 0
    for line in lines:
        if(line.find('DEBUG') != -1 or line.find('INFO') != -1 or line.find('WARN') != -1): 
            count += 1
            doc = { 'file' : file,
                    'time' : line[:19].replace(' ','T'),
                    'level': line[24 : line.find(' ', 25)],
                    'line' : line[line.find(' ', 25):]
            }
            es.index(index="test", doc_type='log',id=filename+"_logline_"+str(count), body=doc)
    print(filename + " : Indexed " + str(count) + " logs")


def indexLogs(dirName) :
   es = Elasticsearch()
   for root, dirnames, filenames in os.walk(dirName):
      for filename in fnmatch.filter(filenames, '*.log'):
        if(filename == "awsapi.log" or filename == "apilog.log" or filename == "management-server.log"):
            readFile(os.path.join(root, filename), filename, es)
   return es

    
			
			
