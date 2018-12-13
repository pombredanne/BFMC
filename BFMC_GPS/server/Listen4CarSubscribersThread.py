import  socket
from    threading import Thread

#================================ LISTEN CAR SUBS =============================
class Listen4CarSubscriberThread(Thread):
    '''Listen4CarSubscriberThread 
    
    This class implementing a server, which waiting on the port to 
    subscriptions.
    Listens for subscription requests from cars and adds car IP in the
    carMap table

    '''
    #================================ INIT ====================================
    def __init__(self,threadID,host_ip,car_subscription_port,carMap,logFile):
        '''__init__ [summary]
        
        Arguments:
            threadID {int}             -- thread identification number
            host_ip {str}              -- host IP address
            car_subscription_port {int}-- port number, wserver is waiting
            carMap {}                  -- container for the data
            logFile {str}              -- logFile 
        '''

        Thread.__init__(self)
        self.name               =   'Listen4CarSubscriberThread'
        self.threadID           =   threadID
        self.host_ip            =   host_ip
        self.runningThread      =   True
        self.carMap             =   carMap
        self.logFile            =   logFile

        self.car_subscription_port  =car_subscription_port
    #================================ RUN =====================================
    def run(self):
        try:
            s = socket.socket()  
            s.bind((self.host_ip, self.car_subscription_port))
            s.listen(255)
            s.settimeout(1.0)

            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' started')
            
            while self.runningThread:
                try:
                    c, addr =  s.accept() 
                    id_b    =  c.recv(1024)
                    id_s    =  str(id_b)	
                    id      =  int(id_s.split("'")[1].split("'")[0])	
                    
                    print("Received id: ",id, '\n',addr[0])

                    self.carMap[id] = (addr[0], "")
                    c.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    print("Failed to receive car ID from car! with error:",e)
        
            s.close()	
            
            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' stoped')	

        except Exception as e:
            self.runningThread = False
            print("Failed to create socket for Car Subscription!")

            if(self.logFile!=None):
                textFile = self.name + ' stoped with exception ' + str(e)
                self.logFile.saveWithDate(textFile)

            s.close()

    #================================ STOP ====================================
    def stop(self):
        self.runningThread = False
