import socket

from    server.Data4CarMap  import *
from    threading           import Thread
from    collections         import namedtuple

#================================ SERVER THREAD ===============================
class ServerThread(Thread):
    '''ServerThread 
    
    This class implements a server, which is collencting from the client the 
    data. Listens for messages from other GPS nodes and updates DATA 
    fields in carMap
    
    '''
    #================================ INIT ====================================
    def __init__(self,threadID,address,carMap,logFile=None):
        '''__init__ 

        Arguments:
            threadID {int}  -- thread identification number
            address {tuple} -- address, where waiting for the clients (IP,PORT)
            carMap {}       -- container for the data
        
        Keyword Arguments:
            logFile {str} -- logFile  (default: {None})
        '''

        Thread.__init__(self)
        self.name           = 'ServerThread'
        self.threadID       = threadID
        self.address        = address
        self.runningThread  = True
        self.carMap         = carMap
        self.logFile        = logFile
    
    #================================ RUN  ====================================
    def run(self):
        '''run server
        '''

        try:			
            print("Starting server")
            server = socket.socket(
                            family  = socket.AF_INET, 
                            type    = socket.SOCK_STREAM
                        )

            server.bind(self.address)
            server.listen(40)
            server.settimeout(4.0)

            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' started')

            while self.runningThread:
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue

                print("Connection established with " + addr[0])

                if(self.logFile!=None):
                    logText = self.name+' connection established with ' + addr[0] 
                    self.logFile.saveWithDate(logText)

                data = conn.recv(1024)
                
                if data:
                    strData = str(data)[2:-1]
                    # split message int individual cars
                    for msg in str(strData).split(';;'):
                        if msg:
                            # get ID and store GPS data
                            carID = int(msg.split(';')[0].split(':')[1])
                            self.carMap[carID] = data4CarStruct(self.carMap[carID][0], msg)
                conn.close()
            
            server.close()
            
            if(self.logFile != None):
                self.logFile.saveWithDate(self.name + ' stopped')
        
        except BaseException as e:
            self.runningThread = False
            if(self.logFile!=None):
                logText = self.name + ' stoped with exception ' + str(e)
                self.logFile.saveWithDate(logText)

    #================================ STOP ==================================== 
    def stop(self):
        self.runningThread = False
