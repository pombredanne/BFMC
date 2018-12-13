import os
import sys
import time
import math
import socket
import random
import threading

from cv2                import  aruco
from threading          import  Thread
from collections        import  namedtuple


class SimulatorClient(Thread):
    def __init__(self,threadID,server_address,logFile):

        Thread.__init__(self)
        self.name               = 'SimulatorClient'
        self.server_address     = server_address
        self.threadID           = threadID
        self.runningThread      = True
        self.logFile            = logFile
    #================================ FWD TO SERVER ===========================
    def ForwardToServer(self,data):
        '''ForwardToServer 

        
        transmit data to server
        
        Arguments:
            data {(pos,orient)} -- tha dataof the detected car
        '''

        # Uncomment for displaying debug message
        # print(self.server_address.asTuple())

        if(self.server_address.ip == '' and self.server_address.port==-1):
            return False
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)
            client.connect(self.server_address.asTuple())
            message = ""
            for idno,posAzm in data:
                pos,azm = posAzm
                message = "%s%s"%(message,"id:{0[0]};Pos:({1.real:.2f}+{1.imag:.2f}j);Azm:({2.real:.2f}+{2.imag:.2f}j);;".format(idno,pos,azm))
                print(message)

            client.send(bytes(message,"UTF-8"))
            client.close()

        except Exception as e:
            client.close()
            self.server_address.ip      =   ''
            self.server_address.port    =   -1

            print('Cannnot send the data to the server. [Exception Thrown]',e)
            if(self.logFile!=None):
                logText = self.name + " Cannnot send the data" + " to the server. [Exception Thrown] %s"%e

                self.logFile.saveWithDate(logText)
            return False
        return True

    #================================ RUN  ====================================
    def run(self):
        '''run 
        
        It's periodically captures a frame and processes it.
        When the server address is setted, transmites data to the server
  
        '''

        if(self.server_address==None):
            print("Server address wasn't initialized!")
            
            if(self.logFile!=None):
                logText = self.name+"Server address wasn't initialized!"
                self.logFile.saveWithDate( logText )
            return

        print('Server address:',self.server_address.asTuple())
        time.sleep(1)

        posList = 0

        try:
            while(self.runningThread):
                # get markers from detector

                if(self.server_address.ip!='' and self.server_address.port>1):
                    t = time.time()
                    for data in self.generateData(posList):
                        isSent = self.ForwardToServer([data])
                        if(not self.runningThread or not isSent):
                            break
                    dt = time.time() - t
                    # Uncomment for displaying debug message
                    # print(dt)
                    if dt < 1:
                        time.sleep(1-dt)
                    t = time.time()
                    posList += 1
                    if posList > 98:
                        posList =  0

        except BaseException as e:
            if(self.logFile!=None):
                self.logFile.saveWithDate(self.name+' stoped with exception'+ str(e))
            print("[Exception Thrown] %s"%e)
    #================================ PTS CIRCLE ==============================
    def points(self, radius,noPoints = 100):
        '''points 
        
        Utility function for generating the points of a circle
        
        Arguments:
            radius {int} -- the radius of the circle
        
        Keyword Arguments:
            noPoints {int} -- the number of points in the circle (default: {100})
        
        Returns:
            list -- list of complex numbers
        '''

        return [  math.cos(2*math.pi/noPoints*x)*radius +
                    (math.sin(2*math.pi/noPoints*x)*radius)*1j
                for x in range(0,noPoints+1)]
    #================================ GEN DATA ================================
    def generateData(self, posList):
        '''generateData 
        
        utility function for packing ids an position/orientation
        
        Arguments:
            posList {int} -- the current index position in the circle list
        
        Returns:
            list -- [[id]][pos+pos_img*j][or+or*j]] 
        '''

        points  =   self.points(100, 100)
        fakeIds =   [i for i in range(30)]
        data = []
        for ids in fakeIds:
            data.append(([ids,], (points[posList], points[posList+1])))

        return data

    #================================ STOP ====================================
    def stop(self):
        self.runningThread=False
