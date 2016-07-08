#!python3
#coding: utf8

import datetime
import time
import json
from datetime import timezone
import sys
import os
import requests
from requests.auth import HTTPBasicAuth
sys.path.insert(1,'C:\opt\integrations\_Python_Scripts\library')
from additionalFunctions import runZenDeskCall
from additionalFunctions import runNetSuiteCall
from additionalFunctions import decodeAttachmentFileType
from additionalFunctions import writeLogFile

newList=[]
importData={}

def main():
  sixtyFiveSecondsAgo=time.time()-90
  yesterday=datetime.date.fromordinal(datetime.date.today().toordinal())
  searchAPI='https://DOMAIN.zendesk.com/api/v2/search.json?query=type:ticket%20tags:update_ns%20status:new%20status:open%20status:pending%20status:hold'
  searchResponse=runZenDeskCall('GET',searchAPI,'')
  if('count' in searchResponse):
    if(searchResponse['count']>0):
      thisCount=0;
      for key in searchResponse['results']:
        if(len(newList)>=10):
          break;
        if(str(key['organization_id'])=='' or str(key['organization_id'])=="null" or str(key['organization_id'])=="None" or str(key['organization_id'])==None):
          removeSendToNetSuiteOnBadTickets_inZenDesk(str(key['id']));
          continue;
        thisCount+=1;
        netSuiteID=''
        lastEditedField=''
        assigneeEmail=''
        orgNetSuiteID=''
        updateNS='False'
        
        for key2 in key['custom_fields']:
          if(str(key2['id'])=='29131158' and (str(key2['value'])!='None' and str(key2['value'])!='')):
            netSuiteID=str(key2['value']);
          elif(str(key2['id'])=='29168077' and (str(key2['value'])!='None' and str(key2['value'])!='')):
            lastEditedField=str(key2['value']);
          elif(str(key2['id'])=='30296138'):
            updateNS=str(key2['value']);
          else:
            continue
          
        if(str(key['assignee_id'])!='None' and str(key['assignee_id'])!=''):
          assigneeEmail=str(getAssigneeEmail(str(key['assignee_id'])))
        
        if(str(key['organization_id'])!='None' and str(key['organization_id'])!=''):
          orgNetSuiteID=str(getOrganizationNetSuiteID(str(key['organization_id'])))
        
        if(updateNS=="True" or updateNS=="true" or updateNS==True):
          key['netSuiteID']=netSuiteID
          key['assigneeEmail']=assigneeEmail
          key['orgNetSuiteID']=orgNetSuiteID
          key['assignee_id']=str(key['assignee_id']);
          key['group_id']=str(key['group_id']);
          ticketCommentData=getTicketComments(str(key['id']))
          key["commentData"]=ticketCommentData
          
          newList.append(key)
        else:
          searchResponse['results'].remove(key)
  if('next_page' in searchResponse):
    if(searchResponse['next_page']!='null' and searchResponse['next_page']!='' and searchResponse['next_page']!='None' and searchResponse['next_page']!=None):
      return main2(searchResponse['next_page'],sixtyFiveSecondsAgo)

def main2(searchAPI,sixtyFiveSecondsAgo):
  if(str(searchAPI)=="None" or str(searchAPI)==None):
    return '';
  searchResponse=runZenDeskCall('GET',searchAPI,'')
  print("count: "+str(searchResponse['count']));
  if('count' in searchResponse):
    if(searchResponse['count']>0):
      thisCount=0;
      for key in searchResponse['results']:
        if(len(newList)>=10):
          break;
        if(str(key['organization_id'])=='' or str(key['organization_id'])=="null" or str(key['organization_id'])=="None" or str(key['organization_id'])==None):
          removeSendToNetSuiteOnBadTickets_inZenDesk(str(key['id']));
          continue;
        thisCount+=1;
        netSuiteID=''
        lastEditedField=''
        assigneeEmail=''
        orgNetSuiteID=''
        updateNS='False'
        
        for key2 in key['custom_fields']:
          if(str(key2['id'])=='29131158' and (str(key2['value'])!='None' and str(key2['value'])!='')):
            netSuiteID=str(key2['value']);
          elif(str(key2['id'])=='29168077' and (str(key2['value'])!='None' and str(key2['value'])!='')):
            lastEditedField=str(key2['value']);
          elif(str(key2['id'])=='30296138'):
            updateNS=str(key2['value']);
          else:
            continue
                
        if(str(key['assignee_id'])!='None' and str(key['assignee_id'])!=''):
          assigneeEmail=str(getAssigneeEmail(str(key['assignee_id'])))
        
        if(str(key['organization_id'])!='None' and str(key['organization_id'])!=''):
          orgNetSuiteID=str(getOrganizationNetSuiteID(str(key['organization_id'])))
        
        if(updateNS=="True" or updateNS=="true" or updateNS==True): #lastUpdated>sixtyFiveSecondsAgo or 
          key['netSuiteID']=netSuiteID
          key['assigneeEmail']=assigneeEmail
          key['orgNetSuiteID']=orgNetSuiteID
          key['assignee_id']=str(key['assignee_id']);
          key['group_id']=str(key['group_id']);
          ticketCommentData=getTicketComments(str(key['id']))
          key["commentData"]=ticketCommentData
          
          newList.append(key)
        else:
          searchResponse['results'].remove(key)
  if('next_page' in searchResponse):
    if(searchResponse['next_page']!='null' and searchResponse['next_page']!='' and searchResponse['next_page']!='None' and searchResponse['next_page']!=None):
      print('moving from main2 to main2')
      return main2(searchResponse['next_page'],sixtyFiveSecondsAgo)

def removeSendToNetSuiteOnBadTickets_inZenDesk(zdID):
  apiURL='https://DOMAIN.zendesk.com/api/v2/tickets/'+str(zdID)+'.json';
  lastEditedBy=str("Integration_"+str(int(time.time())))
  zdID=str(zdID)
  nsData='{"ticket":{"id":"'+zdID+'"}}'
  nsData=json.loads(nsData)
  nsData=json.dumps(nsData)
  nsData=json.dumps(nsData)
  curlCall='c:\opt\curl\curl '+apiURL+' -H "Content-Type: application/json" -d '+nsData+' -v -u "ZENDESK_USER@DOMAIN.COM":"ZENDESK_PASSWORD" -X PUT -k'
  os.system(curlCall)

def getAssigneeEmail(zenDeskID):
  url="https://DOMAIN.zendesk.com/api/v2/users/"+zenDeskID+".json"
  myResponse2=requests.get(url,auth=HTTPBasicAuth("ZENDESK_USER@DOMAIN.COM","ZENDESK_PASSWORD"),verify=True)
  if(myResponse2.ok):
    jData2=json.loads(myResponse2.content.decode('utf-8','replace'))
    return jData2['user']['email'];
  else:
    return "error";

def getOrganizationNetSuiteID(zenDeskID):
  url="https://DOMAIN.zendesk.com/api/v2/organizations/"+zenDeskID+".json"
  myResponse2=requests.get(url,auth=HTTPBasicAuth("ZENDESK_USER@DOMAIN.COM","ZENDESK_PASSWORD"),verify=True)
  if(myResponse2.ok):
    jData2=json.loads(myResponse2.content.decode('utf-8','replace'))
    return jData2['organization']['organization_fields']['netsuite_id'];
  else:
    return "error";

def getTicketComments(zenDeskTicketID):
  url="https://DOMAIN.zendesk.com/api/v2/tickets/"+str(zenDeskTicketID)+"/comments.json"
  myResponse2=requests.get(url,auth=HTTPBasicAuth("ZENDESK_USER@DOMAIN.COM","ZENDESK_PASSWORD"),verify=True)
  commentData={}
  if(myResponse2.ok):
    jData2=json.loads(myResponse2.content.decode('utf-8','replace'))
    if(jData2['count']>0):
      commentCount=0
      for key in jData2['comments']:
        if(str(key['body'])=="" or str(key['body'])=='' or str(key['body'])=='null'):
          continue
        commentData[commentCount]={}
        commentData[commentCount]['id']=str(key['id'])
        commentData[commentCount]['author_id']=getAssigneeEmail(str(key['author_id']))
        commentData[commentCount]['body']=str(key['body'])
        commentData[commentCount]['created_at']=str(key['created_at'])
        commentData[commentCount]['isPublic']=str(key['public'])
        if(key['attachments']):
          commentData[commentCount]['attach']={}
          attachCount=0
          for keyAttch in key['attachments']:
            commentData[commentCount]['attach'][attachCount]={}
            commentData[commentCount]['attach'][attachCount]['content_url']=str(keyAttch['content_url'])
            commentData[commentCount]['attach'][attachCount]['content_type']=decodeAttachmentFileType(str(keyAttch['content_type']))
            commentData[commentCount]['attach'][attachCount]['size']=str(keyAttch['size'])
            commentData[commentCount]['attach'][attachCount]['file_name']=str(keyAttch['file_name'])
            attachCount+=1
        commentCount+=1
      return commentData
    else:
      return {}
  else:
    return {};

def sendToNetSuite(newList):
  netSuiteContactURL='NETSUITE_RESTLET_URL'
  netSuiteResponse=str(runNetSuiteCall('POST',netSuiteContactURL,json.dumps(newList)))
  if(netSuiteResponse!="error" and netSuiteResponse!=''):
    netSuiteFullResponse=netSuiteResponse.split(':::')
    for thisTicket in netSuiteFullResponse:
      if(thisTicket!='' and thisTicket!='null'):
        netSuiteResponse=thisTicket.split('|||',1)
        updateNetSuiteID_inZenDesk(str(netSuiteResponse[1]),str(netSuiteResponse[0]))

def updateNetSuiteID_inZenDesk(zdID,nsID):
  apiURL='https://DOMAIN.zendesk.com/api/v2/tickets/'+str(zdID)+'.json';
  lastEditedBy=str("Integration_"+str(int(time.time())))
  nsID=str(nsID)
  zdID=str(zdID)
  nsData='{"ticket":{"id":"'+zdID+'"}}'
  nsData=json.loads(nsData)
  nsData=json.dumps(nsData)
  nsData=json.dumps(nsData)
  
  curlCall='c:\opt\curl\curl '+apiURL+' -H "Content-Type: application/json" -d '+nsData+' -v -u "ZENDESK_USER@DOMAIN.COM":"ZENDESK_PASSWORD" -X PUT -k'
  os.system(curlCall)

main()
sendToNetSuite(newList)