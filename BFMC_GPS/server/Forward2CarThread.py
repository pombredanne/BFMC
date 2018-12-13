import time
import socket

from threading import Thread

#================================ FWD 2 CAR THREAD ============================
class Forward2CarThread(Thread):
    '''Forward2CarThread 
    
    This class implementing an information distribution system 
    periodically passes through carMap table and if an IP is 
    pressent and DATA was updated, sends DATA field to car at IP field then 
    resets DATA field
    
    '''
    #================================ INIT ====================================
    def __init__(self,threadID,car_communication_port,carMap,period,logFile):
        '''__init__ 
        
        Arguments:
            threadID {int}              -- thread identification number
            car_communication_port {}   -- port number,where server is waiting
            carMap {}                   -- container for the data
            period {int}                -- peried to transmite the data 
            logFile {str}               -- logFile 
        '''

        Thread.__init__(self)
        self.name                   =   'Forward2CarThread'
        self.threadID               =    threadID
        self.car_communication_port =   car_communication_port
        self.runningThread          =   True
        self.carMap                 =   carMap
        self.period                 =   period
        self.logFile                =   logFile

    #================================ RUN =====================================
    def run(self):
        try:		
            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' started')
            
            while self.runningThread:
                for idx in range(255):			# pass through carMap table
                    if self.carMap[idx][0] != "" and self.carMap[idx][1] != "":
    
                        try:
                            s = socket.socket()
                            s.connect((self.carMap[idx][0], self.car_communication_port))
                            s.send(bytes(self.carMap[idx][1], "UTF-8"))
                            s.close()

                            print("Send to car:",   idx, 
                                    "data:" ,       self.carMap[idx][1],
                                    "at IP:",       self.carMap[idx][0]
                                )
                                
                            self.carMap[idx] = data4CarStruct(self.carMap[idx][0], "")
                        
                        except Exception as e:
                            print("Failed to send position data to car! with error: ",e)
                            self.logFile.saveWithDate(self.name+" failed to send position data to car! with error: " + str(e))
                            self.carMap[idx] = data4CarStruct("", "") # reset the ip address and the data field, assuming the client was disconnected
    
                time.sleep(self.period)
    
            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' stoped')
    
        except Exception as e:
            self.runningThread = False
            if(self.logFile != None):
                self.logFile.saveWithDate(self.name+' stoped with exception '+str(e))
    
    #================================ STOP ====================================
    def stop(self):
        self.runningThread=False