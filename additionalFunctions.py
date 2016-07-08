#!python3
#coding: utf8
# utility function file

import csv
import sys
import time
import requests
import json
import urllib
from urllib.parse import quote_plus
from requests.auth import HTTPBasicAuth
import datetime
from datetime import timezone
from datetime import datetime
maxInt=sys.maxsize
decrement=True
while decrement:
    decrement=False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt=int(maxInt/10)
        decrement=True
csv.field_size_limit(maxInt)
import dateutil.parser as parser
import time
def makeItWait(sec):
  time.sleep(sec)
  
zdAuthHeader=HTTPBasicAuth("zenDeskUser@domain.com","ZenDesk_Password")
netSuiteAuthHeader={'Accept':'application/json','Content-Type':'application/json','Authorization':'NLAuth nlauth_account=NETSUITE_ACCOUNT_ID,nlauth_email=NETSUITE_USER@DOMAIN.COM,nlauth_signature="NETSUITE_PASSWORD",nlauth_role=3'}

def fixTimeStamp(timestamp):
    date=(parser.parse(timestamp))
    return str(date.isoformat())

def runZenDeskCall(callType,apiURL,zenDeskData):
  h={'Accept':'application/json','Content-Type':'application/json'}
  if(callType=='GET'):
    myRequest=requests.get(apiURL,auth=zdAuthHeader,verify=True)
  elif(callType=='DELETE'):
    myRequest=requests.delete(apiURL,auth=zdAuthHeader,verify=True)
  elif(callType=='POST'):
    myRequest=requests.post(apiURL,auth=zdAuthHeader,headers=h,data="%s"%json.dumps(zenDeskData))
  elif(callType=='PUT'):
    myRequest=requests.put(apiURL,auth=zdAuthHeader,headers=h,data="%s"%json.dumps(zenDeskData))
  else:
    return "ERROR: Bad CallType"
  if(myRequest.ok):
    jData=json.loads(myRequest.content.decode('utf-8'))
    return jData;
  else:
    try:
      return "ERROR: "+json.dumps(myRequest);
    except Exception as e1:
      return "ERROR[e1]: "+str(e1)+" > "+str(myRequest.content);

def runNetSuiteCall(callType,apiURL,netSuiteData):
  logData=''
  myRequest=requests.post(apiURL,headers=netSuiteAuthHeader,data="%s" % netSuiteData)
  if(myRequest.ok):
    jData=json.loads(myRequest.content.decode('utf-8'))
  else:
    return "error";
  return jData

def decodeAttachmentFileType(x):
  return {
    'image/x-xbitmap':'BMPIMAGE',
    'text/css':'STYLESHEET',
    'text/csv':'CSV',
    'application/msword':'WORD',
    'application/x-autocad':'AUTOCAD',
    'message/rfc822':'MESSAGERFC',
    'image/gif':'GIFIMAGE',
    'application/​x-​gzip-​compressed':'GZIP',
    'text/html':'HTMLDOC',
    'image/ico':'ICON',
    'image/jpeg':'JPGIMAGE',
    'text/javascript':'JAVASCRIPT',
    'video/quicktime':'QUICKTIME',
    'audio/mpeg':'MP3',
    'video/mpeg':'MPEGMOVIE',
    'application/vnd.ms-project':'MSPROJECT',
    'application/pdf':'PDF',
    'image/pjpeg':'PJPGIMAGE',
    'image/x-png':'PNGIMAGE',
    'application/​vnd.​ms-​powerpoint':'POWERPOINT',
    'application/postscript':'POSTSCRIPT',
    'application/rtf':'RTF',
    'application/sms':'SMS',
    'application/​x-​shockwave-​flash':'FLASH',
    'image/tiff':'TIFFIMAGE',
    'text/plain':'PLAINTEXT',
    'application/vnd.visio':'VISIO',
    'application/vnd.ms-excel':'EXCEL',
    'text/xml':'XMLDOC',
    'application/zip':'ZIP'
  }.get(x,'ERROR')

def writeLogFile(fileName,body):
  bodyMessage="*****\n"+str(int(time.time()))+"\n"+body
  with open(fileName, 'r+') as f:
    content=f.read()
    f.seek(0,0)
    f.write(bodyMessage.rstrip('\r\n')+'\n*****\n'+content)
