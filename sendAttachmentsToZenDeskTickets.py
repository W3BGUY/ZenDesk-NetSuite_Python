#!python3
#coding: utf8
import os
import time
import requests
import json
from requests.auth import HTTPBasicAuth
import urllib
import datetime
from datetime import timezone
from datetime import datetime
import random
import time
import glob
import subprocess
import re
zdAuthHeader=HTTPBasicAuth("ZenDeskUser@domain.com","ZenDesk_Password")
processedDir="c:\\opt\\integrations\\attachments\\processed\\"

def main():
  excludes=['c:\\opt\\integrations\\attachments\\FAILED','c:\\opt\\integrations\\attachments\\ignored','c:\\opt\\integrations\\attachments\\missed','c:\\opt\\integrations\\attachments\\processed'] # for dirs and files
  for root,dirs,files in os.walk('c:\\opt\\integrations\\attachments\\'):
    for fname in files:
      if "^.*" in dirs:
        print("skipping "+fname)
        continue;
      print("checking: "+fname);
      
      found=0;
      pathOrig=os.path.join(root,fname)
      if(fname=="finished.pdf"):
        os.remove(pathOrig)
        continue
      
      fname=fname.replace(" ","_")
      pathNew=os.path.join(root,fname)
      try:
        os.rename(pathOrig,pathNew)
      except Exception as e1:
        os.remove(pathOrig)
        fname='';
        continue
            
      fnameLength=len(fname)
      randomNum=str(random.randrange(0,101,2))
      
      if(len([x for x in os.listdir(processedDir) if len(x)>=fnameLength and x[-fnameLength:]==fname])<=0):
        print(fname+" - not there")
      else:
        print(fname+" - it's there")
        os.remove(pathNew)
        fname='';
        continue
      
      nameSplit=fname.split('_',2)
      zenDeskID=nameSplit[0];
      if(zenDeskID in nameSplit[1]):
        print(fname+" / "+str(nameSplit[1])+" / "+str(zenDeskID)+" - bad duplicate")
        os.remove(pathNew)
        fname='';
        continue
      
      token=sendFileToZenDesk(zenDeskID,fname,pathNew)
      if(token=="ERROR"):
        os.rename(pathNew,"c:\\opt\\integrations\\attachments\\FAILED\\"+randomNum+"_"+fname)
        continue
      payload=json.loads('{"ticket":{"comment":{"body":"File Attachment","uploads":["'+token+'"]}}}')
      apiURL='https://DOMAIN.zendesk.com/api/v2/tickets/'+str(zenDeskID)+'.json'
      attachReponse=runZenDeskCall('PUT',apiURL,payload)
      
      if(attachReponse=='SUCCESS'):
        os.rename(pathNew,"c:\\opt\\integrations\\attachments\\processed\\"+randomNum+"_"+fname)
      else:
        os.rename(pathNew,"c:\\opt\\integrations\\attachments\\FAILED\\"+randomNum+"_"+fname)
        print("|"+attachReponse+"|")
        fname=''
      continue
    break
  print("Finished")
  return 1;
  
def sendFileToZenDesk(zdID,fileName,fullPath):
  apiURL=str('https://DOMAIN.zendesk.com/api/v2/uploads.json?filename='+fileName)
  curlCall='c:\opt\curl\curl "'+apiURL+'" -H "Content-Type: application/binary" --data-binary @'+fullPath+' -u "ZenDeskUser@domain.com":"ZenDesk_Password" -X POST -k'
  
  try:
    response=subprocess.check_output(curlCall,shell=True)
  except Exception as e1:
    return "ERROR"
  
  try:
    responseObj=json.loads(removeBOM(response));
  except Exception as e:
    return "ERROR"
  
  return str(responseObj['upload']['token'])

def removeBOM(string):
  return str(string,'utf-8')

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
    return "SUCCESS";
  else:
    return "ERROR";

main()