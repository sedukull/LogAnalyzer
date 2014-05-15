#!/usr/bin/python2.7 


print "Content-type: text/html\n\n"
import sys
sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
sys.path.append("/usr/local/lib/python2.7")
sys.path.append("/usr/local/lib/python2.7/site-packages")
import cgi
import os
from marvinTestResultsHtml import TcResultHtmlView
from startElastic import sendQuery


NFS_PATH= "/root/softwares/BugLogger/nfs_mnt_jenkins_out_log_path"
MACHINE_IP="10.147.38.151"

def get_version_dirs():
    global NFS_PATH
    temp_path = NFS_PATH
    temp_list = ""
    for items in os.listdir(temp_path):
        temp_list = temp_list + '<li><a href="Http://' + str(MACHINE_IP) +'//LogAnalyzer/logAnalyzer.py?cmd=hl&dir=' + str(items) + '">'  + str(items) + '</a></li>'
    to_display = '<html xmlns="http://www.w3.org/1999/xhtml">' + '<head></head><body></ul>' + temp_list  +'</ul></body></html>'
    print to_display

def get_hypervisor_level(inp):
    global NFS_PATH
    temp_path = NFS_PATH + "//" + inp
    temp_list = ""
    for items in os.listdir(temp_path):
        temp_list = temp_list + '<li><a href="Http://' + str(MACHINE_IP) +'//LogAnalyzer/logAnalyzer.py?cmd=bl&dir=' + str(inp)+ "//" + str(items) + '">'  + str(items) +'</a></li>'
    to_display = '<html xmlns="http://www.w3.org/1999/xhtml">' + '<head></head><body></ul>' + temp_list  +'</ul></body></html>'
    print to_display  
    
def get_build_info(inp):
    global NFS_PATH
    temp_path = NFS_PATH + "//" + inp
    temp_list = ""
    for items in os.listdir(temp_path):
        temp_list = temp_list + '<li><a href="Http://' + str(MACHINE_IP) +'//LogAnalyzer/logAnalyzer.py?cmd=getResults&dir=' + str(temp_path) + "/" + str(items) + '">' + str(items) + '</a></li>'
    to_display = '<html xmlns="http://www.w3.org/1999/xhtml">' + '<head></head><body></ul>' + temp_list  +'</ul></body></html>'
    print to_display  


def get_results_info(inp):
    obj = TcResultHtmlView(inp, "/tmp/t.log")
    out = obj.generateHtmlView()
    print out

def get_log_info(st,et):
    out = sendQuery(st,et) 
    print out

def main():
    fields = cgi.FieldStorage()
    if not len(fields.keys()):
        get_version_dirs()
    else:
        if  fields["cmd"].value == "hl":
            get_hypervisor_level(fields["dir"].value)
        if  fields["cmd"].value == "bl":
            get_build_info(fields["dir"].value)
        if  fields["cmd"].value == "getResults":
            get_results_info(fields["dir"].value)
        if  fields["cmd"].value == "getLogInfo":
            get_log_info(fields["st"].value,fields["et"].value)

main()
