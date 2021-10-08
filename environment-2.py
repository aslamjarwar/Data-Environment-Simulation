import pika
import sys
import json
import time
import os
import prov.model as prov
from datetime import datetime,timedelta,date

activity_ls={}
entity_ls={}
path='D:\\UoM\\OneDrive - The University of Manchester\\PROVANON\\PROV_Coding\hello_world\\'
#####Generate graph for NRDS
dc = {
    "contract": {
        "DC": "NRDS",
         "contract_id":"DGI002",
        "Address": "New York,Post code AA",
        "Purpose":"NewDataList"
        
    }
}

 

reqData = {
    "reqData": {
        "contract_id":"DGI002",
        "sessionID": ""
                
    }
}

dc_json=json.dumps(dc) # convert into JSON
reqData_json=json.dumps(reqData) # convert into JSON
class Nrds:
    
    def __init__(self):
        print()
    def getConnection(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        return connection
    
    def getChannel(self,connection,queu):
        channel = connection.channel()
        #center_id='center_y_001'
        channel.queue_declare(queue=queu)
        return channel
        
        
    def sendData(self,queue,dataToSend):
        connection=self.getConnection()
        channel=self.getChannel(connection=connection,queu=queue)
        channel.basic_publish(exchange='', routing_key=queue, body=dataToSend)
        print(" [x] Data Request   %r" % dataToSend)
        connection.close()
    
    def callback(self,ch, method, properties, body):
        encoding = 'utf-8'
        dataFrmEnv=body.decode(encoding)
        
        print(" [x] Received %r" % dataFrmEnv)
        pr=""
        for q in range(2):
            for m in range(q+1):
                time.sleep(1)
                pr+="---"
                print(pr)
            print("")

        self.parse(dataFrmEnv)
        
    def consume(self,queue):
        connection=self.getConnection()
        channel=self.getChannel(connection=connection,queu=queue)
        channel.basic_consume(queue=queue, on_message_callback=self.callback, auto_ack=True)
        print(' [*]  To stop service press CTRL+C')
        channel.start_consuming()
        
    def parse(self,data):
        data = json.loads(data) # parse json data
        element=""
        sid=0
        for key in data:
            element=key
        if(element=="session"):
            sid=data[key]['sessionID']
            contractId=data[key]['contract_id']
            ac=bundle.activity("receive_"+self.getTime(),other_attributes={"prov:sessionId*":sid,
                                                                "prov:contract_id*":contractId})
            
            bundle.wasStartedBy(ac,trigger=activity_ls.get("sendContract_"))
            en=bundle.entity("sid_"+self.getTime(),{"prov:sessionId*":sid})
            bundle.wasGeneratedBy(en,ac)
            if(len(str(sid)) !=0 and contractId=="DGI002"):
                print ('session id and contract id done...')
                time.sleep(2)
                print("requesting data from gond...........")
                time.sleep(2)
                reqData["reqData"]["sessionID"]=sid
                reqData_json=json.dumps(reqData)
                #print (reqData_json)
                self.sendData(queue='ADF',dataToSend=reqData_json)
                ac_233=bundle.activity("dataRequest_"+self.getTime(),other_attributes={"prov:sessionId*":sid,
                                                                "prov:contract_id*":contractId})
                bundle.used(ac_233,en)
                bundle.used(ac_233,entity_ls.get("phyActivityDataset"))
                activity_ls.update({"dataRequest_":ac_233})
            else:
                return
        elif(element=="phyAcDataSet"):
            ac_234=bundle.activity("receive_"+self.getTime(),other_attributes={"prov:desc*":"receiving required dataset"})
            
            bundle.wasStartedBy(ac_234,trigger=activity_ls.get("dataRequest_"))
            en_235=bundle.entity("phyActivityDataset_"+self.getTime(),{"prov:dec*":"dataset contains top 5 rows from master dataset"})
            bundle.wasGeneratedBy(en_235,ac_234)
            dataset=data.get("phyAcDataSet")
            print(dataset)
            
        else:
            return
        
    def saveProvenanceGraph(self):        
        print("saving provenance document.........")
        time.sleep(3)
        file = open(path+"nrds_Provenance.txt", "w")
        print(path+"nrds_Provenance.txt")
        file.write(document.get_provn())
        file.close()
        from prov.dot import prov_to_dot
        dot = prov_to_dot(document)
        dot.write_png(path+"nrds_Provenance.png")
    
    def getTime(self):
         now = datetime.now()
         dt_string = now.strftime("%d%m%Y%H%M%S")
         return dt_string


if __name__ == '__main__':
    
    document = prov.ProvDocument()
    document.add_namespace('env','https://adf.org/')
    document.add_namespace('dcterms','http://purl.org/dc/terms/')
    bundle=document.bundle('env:nrds')
    bundle.set_default_namespace('https://adf.org/nrds/')
    ac=bundle.activity('search')
    bundle.wasAssociatedWith(ac,bundle.agent('nrds',
                                             {"prov:type":"DataController"}))
    ns=Nrds()
    dataToSend=dc_json       
    en=bundle.entity("contract_"+ns.getTime(),
               {"prov:type":"Entity",
                "prov:description*":"contract"})
    ac1=bundle.activity("sendContract_"+ns.getTime())
    bundle.wasStartedBy(ac1,ac)
    bundle.used(ac1,en)
    #bundle.wasInformedBy(ac1, ac)  
    en=bundle.entity("phyActivityDataset_"+ns.getTime(),{
                                       "prov:type":"Entity",
                                       "dcterms:title":"Available Physical Activty dataset"})
    bundle.wasGeneratedBy(en,ac)
    activity_ls.update({"sendContract_":ac1})
    
    entity_ls.update({"phyActivityDataset":en})
    time.sleep(1)    
    try:
        ns.sendData(queue='ADF',dataToSend=dataToSend)
        ns.consume("ADF0")
    except KeyboardInterrupt:
        print('Interrupted')
    try:
        ns.saveProvenanceGraph()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    


#connection = pika.BlockingConnection(
  #  pika.ConnectionParameters(host='localhost'))
    
#channel = connection.channel()
#center_id='center_y_001'
#channel.queue_declare(queue='ADF')
#data_x =input('Please input data to send :',);
#data_x=center_id+ '@ has sent '+data_x
#channel.basic_publish(exchange='', routing_key='ADF', body=dc_json)
#print(" [x] Data Request   %r" % dc_json)
#connection.close()

 # parse x:
y = json.loads(dc_json)   
#dc2=json.loads(dc_json)
#print(y['contract']['DC'])
#for key in y:
 #   print(key)