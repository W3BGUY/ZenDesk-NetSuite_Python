#!python3
#coding: utf8
import datetime
import time
import json
from datetime import timezone
import sys
sys.path.insert(1,'C:\opt\integrations\_Python_Scripts\library')
from additionalFunctions import runZenDeskCall
from additionalFunctions import runNetSuiteCall
newList=[]

def main():
  sixtyFiveSecondsAgo=time.time()-75
  today=datetime.date.fromordinal(datetime.date.today().toordinal())
  searchAPI='https://DOMAIN.zendesk.com/api/v2/search.json?query=type:organization%20tags:update_ns'
  searchResponse=runZenDeskCall('GET',searchAPI,'')
  if('count' in searchResponse):
    if(searchResponse['count']>0):
      for key in searchResponse['results']:
        if(str(key['organization_fields']['netsuite_id'])!='None' and str(key['organization_fields']['netsuite_id'])!=''):
          lastUpdated=int(time.mktime(time.strptime(str(datetime.datetime.strptime(str(key['updated_at']).replace('T',' ').replace('Z',''),"%Y-%m-%d %H:%M:%S")),"%Y-%m-%d %H:%M:%S")))-21600
          if(str(key['organization_fields']['update_ns'])=="True"): 
            newList.append(key)
            continue
  if('next_page' in searchResponse):
    if(searchResponse['next_page']!='null' and searchResponse['next_page']!='' and searchResponse['next_page']!='None' and searchResponse['next_page']!=None):
      return main2(searchResponse['next_page'],sixtyFiveSecondsAgo)

def main2(searchAPI,sixtyFiveSecondsAgo):
  if(str(searchAPI)=="None" or str(searchAPI)==None):
    return '';
  searchResponse=runZenDeskCall('GET',searchAPI,'')
  if('count' in searchResponse):
    if(searchResponse['count']>0):
      for key in searchResponse['results']:       
        lastUpdated=int(time.mktime(time.strptime(str(datetime.datetime.strptime(str(key['updated_at']).replace('T',' ').replace('Z',''),"%Y-%m-%d %H:%M:%S")),"%Y-%m-%d %H:%M:%S")))-21600
        if(str(key['organization_fields']['update_ns'])=="True"): 
          newList.append(key)
  if('next_page' in searchResponse):
    if(searchResponse['next_page']!='null' and searchResponse['next_page']!='' and searchResponse['next_page']!='None' and searchResponse['next_page']!=None):
      return main2(searchResponse['next_page'],sixtyFiveSecondsAgo)

def sendToNetSuite(newList):
  if(newList):
    netSuiteContactURL='NETSUITE_RESTLET_URL'
    netSuiteResponse=runNetSuiteCall('POST',netSuiteContactURL,json.dumps(newList))

main()
sendToNetSuite(newList)