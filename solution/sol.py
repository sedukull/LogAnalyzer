from elasticsearch import Elasticsearch
import glob
import fnmatch
import os
import sys

es = Elasticsearch()

def readFile(filename, file):
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
    print(filename + " : Indexed " + str(count) + " logs");


def searchLogs(dirName) :
   for root, dirnames, filenames in os.walk(dirName):
      for filename in fnmatch.filter(filenames, '*.log'):
        if(filename == "awsapi.log" or filename == "apilog.log" or filename == "management-server.log"):
            readFile(os.path.join(root, filename), filename)



if __name__=="__main__":
    searchLogs(sys.argv[1])
