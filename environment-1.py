import pika
import sys
import os
from datetime import datetime,timedelta,date
import time
import random
from faker import Faker
import pandas as pd
import json 
import prov.model as prov

df = pd.DataFrame()


class Environment_1:
    
    def __init__(self):
        self.fake=Faker()
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()        
        self.channel.queue_declare(queue='ADF')
        self.EnvironmentsId={}
    
    def callback(self,ch, method, properties, body):
        encoding = 'utf-8'
        dataFrmEnv=body.decode(encoding)
        print(" [x] Received %r" % dataFrmEnv)
        self.buildProvenanceGraph(dataFrmEnv)
        
    
    def dataService(self):
        self.channel.basic_consume(queue='ADF', on_message_callback=self.callback, auto_ack=True)    
        print(' [*] Data Service is started. To stop service press CTRL+C')
        self.channel.start_consuming()
        
    def dob(self):
        #https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
        start_date = date(1990, 1, 1)
        end_date = date(2005, 2, 1)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date
  
    def name(self):
        #https://stackoverflow.com/questions/40921767/generate-list-of-random-names-python
        first_names=('John','Andy','Joe')
        last_names=('Johnson','Smith','Williams')
        full_name=random.choice(first_names)+" "+random.choice(last_names)
        return full_name;
    
    def walkTime(self):
        start = datetime.strptime('1/1/2018 1:30 PM', '%m/%d/%Y %I:%M %p')
        end = datetime.strptime('1/1/2018 3:30 PM', '%m/%d/%Y %I:%M %p')
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        #return start + timedelta(seconds=random_second)
        return round(random_second/60,2)

    
    
        

    def syntheticData(self):
        cols=['name', 'dob', 'address', 'jogging']
        lst=[]
        
        for i in range(50):
            lst.append([ins.name(),ins.dob(),ins.fake.address(),ins.walkTime()])
        df = pd.DataFrame(lst, columns=cols)
        df.to_csv('data.csv')
        print("Generating synthetic dataset.........")
        time.sleep(3)  
        print(df)
        return df
        
    def contractVerification(self,dc, contractId):
                  
        if(len(contractId)!=0 ):
            for key in self.EnvironmentsId:
                if(key==contractId):
                    return self.EnvironmentsId.get(key)
        else:
            print ("............")
        if(len(contractId)!=0 ):
            transacId=random.randrange(100, 999)
            self.EnvironmentsId.update({contractId:transacId})
            return transacId
        else:
            return False
        
        
    def buildProvenanceGraph(self,dataFrmEnv):
        print ('building provence graph.........')
        data = json.loads(dataFrmEnv) # parse json data
        element=""
        for key in data:
            element=key
        if(element=="contract"):
            dc=data[key]['DC']
            contractId=data[key]['contract_id']
            ac=bundle.activity("contract_validation_"+self.getTime(),'2021-05-12 14:15','2021-05-12 14:16',{'prov:contract_id*':contractId})
            bundle.used(ac,bundle.entity('contracts_'+self.getTime()))
            print ('verifying contracts.........')
            transcId=self.contractVerification(dc,contractId)
            time.sleep(3)
            e1=bundle.entity("sessionId_%s" %transcId+"_"+self.getTime())
            bundle.wasGeneratedBy(e1,ac)
            bundle.wasStartedBy('advertise', trigger=ac)
            print ('sending code for next processing.....')
            datases = {
           "session": {
           "DC": dc,
          "contract_id":contractId,
          "sessionID": transcId
            }
            }
            datases=json.dumps(datases)
            self.sendData(datases)
            ac=bundle.activity("Send_ID_"+self.getTime(),'2021-05-12 14:15','2021-05-12 14:16',{'prov:contract_id*':contractId})
            bundle.used(ac,e1)
            time.sleep(3)
            
        elif (element=="reqData"):
            contractId=data[key]['contract_id']
            sid=data[key]['sessionID']
            if(len(str(sid)) !=0 and contractId=="DGI002"):
                self.EnvironmentsId.get(contractId)
                if(self.EnvironmentsId.get(contractId)==sid):
                    print('data requestion session id %r verified '%sid)
                    time.sleep(3)
                    print("preparing data for sharing.........")
                    time.sleep(3)                    
                    ls={}
                    derivData=pd.read_csv(os.getcwd()+"\\data.csv",index_col=0).head(5).to_dict()
                    derivData=json.dumps(derivData) #coverting to json
                    derivData=json.loads(derivData) #parsing with json
                    ls.update({"phyAcDataSet":derivData})
                    derivData=json.dumps(ls)
                    print("Data preparation done.........")
                    e_phy=bundle.entity("phyActivityDataset_"+self.getTime(),{
                                       "prov:type":"Entity",
                                       "prov:sessionId*":sid,
                                       "prov:contract_id*":contractId,
                                       "dcterms:title":"Physical Activty derive dataset"
                                       })
                    print("...................................................")
                    bundle.wasDerivedFrom(e_phy, "phyActivityDataset")
                    ac_share=bundle.activity("share_"+self.getTime(),'2021-05-12 14:15','2021-05-12 14:16',{"prov:sessionId*":sid,
                                                                "prov:contract_id*":contractId})
                    bundle.used(ac_share,e_phy)
                    time.sleep(2)
                    self.sendData(derivData)
                    print("Data sending completed.........")
                else: 
                    return
              
            else:
                return
            
             
        else:
             print('nothing received')
            

        center_id=dataFrmEnv[0]
        time.sleep(3)  
        
        entity_id='en_'+dataFrmEnv[0]+'_'+self.getTime()
       
        if(center_id=="center_x_001"):
            if(self.isFirstTime):
                activity_id='dataCollection__'+dataFrmEnv[0]+'_'+self.getTime()
                a1=center_x.activity(activity_id)
                ag=center_x.agent('exeAgent',{"prov:type": "software"})
                center_x.wasAssociatedWith(a1,ag)
                time.sleep(3)            
                e1_center_x=center_x.entity(entity_id,{"dataset:subjectId":self.subId(),
                                                       "dataset:admission_type":'EMERGENCY',
                                                       "dataset:ethnicity":"Un known",
                                                       "dataset:admittime":self.getTime()})
                center_x.wasGeneratedBy(e1_center_x,a1)
                
                activity_id='dataCleaning__'+dataFrmEnv[0]+'_'+self.getTime()
                a1=center_x.activity(activity_id)
                center_x.used(a1,e1_center_x)
                e1_center_x=center_x.entity('en_'+dataFrmEnv[0]+'_'+self.getTime(),
                                            {"dataset:subjectId":self.subId(),
                                                       "dataset:admission_type":'EMERGENCY',
                                                       "dataset:ethnicity":"Un known",
                                                       "dataset:admittime":self.getTime()})
                center_x.wasGeneratedBy(e1_center_x,a1)
                
                self.prev_entity_id_center_x=e1_center_x
                self.isFirstTime=False
                
            else:
                e2=center_x.entity(entity_id,{"dataset:subjectId":self.subId(),
                                                       "dataset:admission_type":'EMERGENCY',
                                                       "dataset:ethnicity":"Un known",
                                                       "dataset:admittime":self.getTime()})
                center_x.wasDerivedFrom(e2,self.prev_entity_id_center_x)
                self.prev_entity_id_center_x=e2
        
    
    def getTime(self):
         now = datetime.now()
         dt_string = now.strftime("%d%m%Y%H%M%S")
         return dt_string
     
    def sendData(self,data):
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))    
        channel = connection.channel()
        channel.queue_declare(queue='ADF0')
        #data_json=json.dumps(data) # convert into JSON
        channel.basic_publish(exchange='', routing_key='ADF0', body=data)
        print("session id sending completed......")
        connection.close()
        
    def saveProvenanceGraph(self):
        path='D:\\UoM\\OneDrive - The University of Manchester\\PROVANON\\PROV_Coding\hello_world\\'
        print("saving provennce document.........")
        time.sleep(3)
        file = open(path+"gond_Provenance.txt", "w")
        file.write(document.get_provn())
        file.close()
        from prov.dot import prov_to_dot
        dot = prov_to_dot(document)
        dot.write_png(path+'gond_Provenance.png')
    
    def test(self):
        d={}
        d["dataset"]=df.head(1).to_dict()
        #js=df.head(1).to_json(orient = 'records')
        print(d)
        from io import StringIO
        bb=StringIO()
        df.to_json(path_or_buf=bb,orient='records')
        dfJson=json.loads(str(bb))

        print(dfJson)
        os._exit(0)

if __name__ == '__main__':
    ins=Environment_1()
    df=ins.syntheticData()
    #ins.test()
    
    # print(type(d))
    # #data = json.loads(js) # parse json data
    # #print(data)
    
    document = prov.ProvDocument()
    document.add_namespace('env','https://adf.org/')
    document.add_namespace('dcterms','http://purl.org/dc/terms/')
    bundle=document.bundle('env:gond')
    bundle.set_default_namespace('https://adf.org/gond/')
    ac=bundle.activity('advertise')
    bundle.wasStartedBy(ac,bundle.agent('gond',
                                             {"prov:type":"DataController"}))
    en=bundle.entity("phyActivityDataset",{"prov:host*":"192.168.0.1",
                                       "prov:type":"Entity",
                                       "dcterms:title":"Physical Activty dataset"})
    bundle.wasGeneratedBy(en,ac)  
    
    try:
        ins.dataService()
    except KeyboardInterrupt:
        print('Interrupted')
    try:
        ins.saveProvenanceGraph()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    
   
    
   
# =============================================================================
# def sendData(self,data):
#         connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host='localhost'))
#         channel = connection.channel()
#         env_id='environemnt_x_001'
#         channel.queue_declare(queue='ADF')
#         #data_x =input('Please input data to send :',);
#         #data_x=env_id+ '@ has sent '+data_x
#         channel.basic_publish(exchange='', routing_key='ADF', body=data)
#         print(" [x] data sent   %r" % data)
#         connection.close()
# =============================================================================
