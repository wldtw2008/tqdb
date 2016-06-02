#!/usr/bin/python
import time
import sys
import time
import datetime
import os
import urllib

def getQueryStringDict(querystrings):
	mapQS={}
	for qs in querystrings.split("&"):
		if qs.find("=") <= 0: continue
		mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
	return mapQS
