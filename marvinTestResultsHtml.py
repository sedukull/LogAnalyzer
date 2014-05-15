#!/usr/bin/python2.7

print "Content-type: text/html\n\n"

import sys
sys.path.append("/usr/lib/python2.7")
sys.path.append("/usr/lib/python2.7/site-packages")
from xunitparser import parse
#from jira.client import JIRA
import gzip
import os
import zlib
import time
import logging
import smtplib
import HTML
import random
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from marvinBugLoggerDal import TcSearchLocalDb
from optparse import OptionParser
from startElastic import indexLogs

class TcResultHtmlView:

    def __init__(self, buildTestFolder , logger):
        self.__buildTestOutFolder = buildTestFolder
	self.__buildTestsUnzipFolder = "/tmp/"+str(random.randrange(1,10000))
	self.__ts = None
        self.__tr = None
        self.__logger = logger
        self.__xunitOutFolder = None
	self.__tcResultsPath = None
        self.__tcRunPath = None

    def generateHtmlView(self):
	try:
            if (self.unzipTestResult() == Codes.SUCCESS):
                self.__xunitOutFolder = self.__tcResultsPath
                try:
                    indexLogs(self.__buildTestsUnzipFolder)
                except Exception,e:
                    print "=== Indexing logs failed"
            else:
                #self.__logger.debug(
                #    "\nExtracting Test Results Failed")
                return Codes.FAILED 
            #self.__logger.debug(
            #    "=== Test Results Folder : %s===" %
            #    self.__xunitOutFolder)
	    """Create html table with rows 'SNo', 'TCName', 'Result','Time'"""
	    t = HTML.Table(header_row=['SNo', 'TCName', 'Result', 'RunTime', 'StartTime', 'EndTime'])
            test_suites = []	
	    no = 1	
            result_colors = {
                       'success':    'lime',
                       'failure':    'red',
                       'error':      'yellow',
                       'skipped':    'grey',
                }
            #import pdb;pdb.set_trace()
            if self.__xunitOutFolder:
                if os.path.isdir(self.__xunitOutFolder):
		    for items in os.listdir(self.__xunitOutFolder):
                        if os.path.isfile(self.__xunitOutFolder + "/" + items) and items.startswith("test") and items.endswith("xml"):
                            test_suites.append(items)
                for files in test_suites:
                    with open(self.__xunitOutFolder + "/" + files) as f:
                        self.__ts, self.__tr = parse(self.__xunitOutFolder + "/" + files)
                    suite_file = files.split('.xml')[0]
                    suite_file_path = self.__tcRunPath + "/" + suite_file
                    os.mkdir(suite_file_path)
                    if (self.deCompress(suite_file_path + ".zip", suite_file_path) == Codes.SUCCESS):
                        for root, dirs, files in os.walk(suite_file_path):
                            if 'runinfo.txt' in files:
                                run_info = suite_file_path + "/" + "runinfo.txt"
                                break
                            else:
                                return Codes.FAILED
                    pattern = 'TestCaseName:.*Result'
                    run_times = self.grepStartEndTimes(pattern, run_info)
                    #if (run_times == Codes.FAILED):
                    #    print "\nFailed to get the start and end times from runinfo.txt"
                    #     return Codes.FAILED
                    for tc in self.__ts:
                        startTime = run_times[tc.methodname][0]
                        endTime = run_times[tc.methodname][1]
                        color = result_colors[tc.result.lower()]
                        if (tc.result.lower() == 'failure' or tc.result.lower() == 'error'):
                            url = 'http://10.147.38.151//LogAnalyzer/logAnalyzer.py?cmd=getLogInfo&st='+startTime+'&et='+endTime
                            link = HTML.link(tc.result, url)
                            colored_result = HTML.TableCell(link, bgcolor=color)
                        else:
                            colored_result = HTML.TableCell(tc.result, bgcolor=color)
		        t.rows.append([no, tc.classname+"_"+tc.methodname, colored_result, tc.time.total_seconds(), startTime, endTime])
			no = no + 1
            return t
	except Exception as e:
	    #self.__logger.debug(
            # 	"\nParsing Xunit Test Output Failed : %s" % 
            #    Codes.GetDetailExceptionInfo(e))
	    return Codes.FAILED
    
    def deCompress(self, file_to_decompress, out_path):
        try:
            if file_to_decompress and file_to_decompress != '':
                cmd = "unzip " + file_to_decompress + " -d" + out_path
                os.system(cmd)
                return Codes.SUCCESS
            return Codes.FAILED
        except Exception as e:
            #self.__logger.debug(
            #    "\n=========DeCompression failed: %s ====" %
            #    Codes.GetDetailExceptionInfo(e)
            return Codes.FAILED

    def unzipTestResult(self):
        try:
            if (self.deCompress(self.__buildTestOutFolder, self.__buildTestsUnzipFolder) == Codes.SUCCESS):
                for root, dirs, files in os.walk(self.__buildTestsUnzipFolder):
                    if 'test_results.zip' in files:
                        self.__tcResultsPath = root + "/" + "test_results"
                        os.mkdir(self.__tcResultsPath)
                        if self.deCompress(root + "/" + "test_results.zip", self.__tcResultsPath) == Codes.SUCCESS:
                            #self.__logger.debug(
                            #    "==== DeCompressing the test results Successful ====")
                            break
                for root, dirs, files in os.walk(self.__buildTestsUnzipFolder):
                    if 'test_run.zip' in files:
                        self.__tcRunPath = root + "/" + "test_run"
                        os.mkdir(self.__tcRunPath)
                        if self.deCompress(root + "/" + "test_run.zip", self.__tcRunPath) == Codes.SUCCESS:
                            break
                return Codes.SUCCESS
        except Exception as e:
            #self.__logger.debug(
            #        "\n===Unzipping Test Results Failed===")
            return Codes.FAILED

    def grepStartEndTimes(self, pattern, file):
        test_runs = {}
        with open(file) as f:
            run_info = f.read()
            matched_runs = re.findall(pattern, run_info)
            if matched_runs and len(matched_runs) > 0:
                for runs in matched_runs:
                    key = runs.split(';')[0].split(':')[1].strip()
                    startTime = runs.split(';')[2].split(': ')[1]
                    endTime = runs.split(';')[3].split(': ')[1]
                    test_runs[key]=[startTime, endTime]
                return test_runs
            else:
                #print "\n===Did not find the pattern in the run_info.txt file===="
                return Codes.FAILED

class Codes:
    STARTED = "started"
    FAILED = "failed"
    SUCCESS = "success"
    FINISH = "finished"
    STOPPED = "stopped"
    EXCEPTION_OCCURRED = "Exception Occurred"
    LogBugs = "LogBugs"
    DeleteBugs = "DeleteBugs"
    GetJobStatus = "GetJobStatus"
    OPEN = "open"
    REOPEN = "reopen"
    NA = "Not Applicable"

    @staticmethod
    def GetDetailExceptionInfo(e):
        if e is not None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return str(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
        else:
            return Codes.EXCEPTION_OCCURRED

    @staticmethod
    def GetCustomCodes(key):
        customfield_dict = {"severity": {"customfield_10001": "Normal"},
                           "DefectSource" :{"customfield_10803":"Internal"},
                           "Regression":{"customfield_10801" : "Yes"}}

        for k,value in customfield_dict.keys():
            if k == key:
                return value
        return None

