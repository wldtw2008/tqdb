#!/usr/bin/python
import urllib

def getQueryStringDict(querystrings):
	mapQS={}
	for qs in querystrings.split("&"):
		if qs.find("=") <= 0: continue
		mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
	return mapQS

def readProfile():
    profile={}
    with open('/etc/profile.d/profile_tqdb.sh', 'r') as f:
        tmpLines = [l.strip() for l in f.readlines()]
        for l in tmpLines:
            if l.find('export') < 0 : continue
            try:
                (k,v) = l.split(' ')[1].split('=')
            except:
                continue
            profile[k.strip()] = v.strip()
    return profile

