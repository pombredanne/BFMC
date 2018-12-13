import os
import sys
import math
import socket
import random
import threading

from cv2                import  aruco
from threading          import  Thread
from collections        import  namedtuple

from server.Data4CarMap                 import *
from server.Forward2CarThread           import *
from server.Listen4CarSubscribersThread import *
from server.ServerBeaconThread          import *
from server.ServerThread                import *
from server.ThreadSafeFileWriter        import *

class ServerThreadManager(Thread):
    '''
        A server thread manager functionality
        
        It periodically verifies the server thread's state, in the case of 
        blocking it restarts the thread.
    '''


    def __init__(self, threadID, server_address, broadcast_ip, host_ip,
                    negotiation_port, subscription_port, car_subscription_port,
                    car_communication_port, max_wait_time_for_server, 
                    logFile = None
                     ):
        '''
        Decide which simulated GPS starts the server.
        
        Arguments:
            threadID {int}                      -- the thread id
            server_address {str}                -- the server address
            broadcast_ip {str}                  -- broadcast IP address
            host_ip {str}                       -- localhost IP address
            negotiation_port {int}              -- negotiation port 
            subscription_port {int}             -- subscription port used to 
                                                 transmite the data from the 
                                                 detectors to the server
            car_subscription_port {int}         -- port used for the vechile 
                                                 client to subscribe on the 
                                                 server
            car_communication_port {int}        -- port used for trasmiting the 
                                                 data from the server to the 
                                                 clients
            max_wait_time_for_server {float}    -- maximum waiting time to 
                                                 receive a beacon from 
                                                 the server
        
        '''

        Thread.__init__(self)
        self.name                     =   'ServerManager'
        self.threadID                 =   threadID
        self.logFile                  =   logFile

        self.server_address           =   server_address
        self.beacon_thread            =   None
        self.server_thread            =   None
        self.forwarding_thread        =   None
        self.carSubscriber_thread     =   None
        self.carMap                   =   None

        self.broadcast_ip             =  broadcast_ip
        self.host_ip                  =  host_ip
        self.negotiation_port         =  negotiation_port
        self.subscription_port        =  subscription_port
        self.car_subscription_port    =  car_subscription_port
        self.car_communication_port   =  car_communication_port
        self.max_wait_time_for_server =  max_wait_time_for_server

        self.runningThread            =   True

    #================================ NEGOTIATION SERVER  =====================  
    def NegotiateServer(self):
        '''
            Function that decides which simulated GPS starts the server.
        '''

        print("Negotiation start!")
        s = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
        s.bind(('', self.negotiation_port))
        s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        randTime  = 10 * self.max_wait_time_for_server *random.random()
        wait_time = 2 + math.floor(randTime)/100

        print("Waiting " + str(wait_time) + " seconds for server")

        t       =   time.time()
        server  =   []
        try:
            # listen for server broadcast
            s.settimeout(wait_time)	
            data, SERVER_IP = s.recvfrom(1500, 0)
            # server beacon received
            s.close()
            print ("Server started on " + str((SERVER_IP[0])))

            # store server info
            self.server_address.ip      =   str(SERVER_IP[0])
            self.server_address.port    =   self.subscription_port
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
        except Exception as e:
            print("No response, starting server here", e)
            s.sendto(   bytes(self.host_ip , "UTF-8"), 
                        (self.broadcast_ip,self.negotiation_port)
                )
            s.close()

            self.stopAllThread()
            
            self.server_address.ip = self.host_ip
            self.server_address.port = self.subscription_port
            if(self.logFile!=None):
                log_message = 'NegotiateServer- server address %s'%str(self.server_address)
                self.logFile.saveWithDate(log_message)
            
            self.carMap=Data4CarMap(256)

            # thread responsible for broadcasting itself as the server
            self.beacon_thread = ServerBeaconThread(
                            threadID         = self.threadID+1,
                            host_ip          = self.host_ip,
                            broadcast_ip     = self.broadcast_ip,
                            negotiation_port = self.negotiation_port,
                            sleepDuration    = 1.9,
                            logFile          = self.logFile
                        )
            self.beacon_thread.start()

            # thread responsible for collecting GPS data from clients
            self.server_thread = ServerThread(
                            threadID = self.threadID+2,
                            address  = self.server_address.asTuple(),
                            carMap   = self.carMap,
                            logFile  = self.logFile
                        )
            self.server_thread.start()

            # thread responsible for sending GPS data to each registered vehicle
            self.forwarding_thread = Forward2CarThread(
                            threadID    = self.threadID + 3,
                            car_communication_port = self.car_communication_port,
                            carMap      = self.carMap,
                            period      = 1.0,
                            logFile     = self.logFile    
                        )
            self.forwarding_thread.start()

            # thread responsible for registering vehicles
            self.carSubscriber_thread = Listen4CarSubscriberThread(
                            threadID    =  self.threadID + 4, 
                            host_ip     =  self.host_ip, 
                            car_subscription_port = self.car_subscription_port, 
                            carMap      =  self.carMap, 
                            logFile     =  self.logFile
                        )
            self.carSubscriber_thread.start()

        print(str(time.time()-t) + " seconds elapsed")
    
    #================================ STOP ====================================
    def stopAllThread(self):
        '''
            Function responsible for stoppinf all threads
        '''
        #beacon thread
        if self.beacon_thread != None:
            self.beacon_thread.stop()
            if(self.beacon_thread.is_alive()):
                self.beacon_thread.join()
                self.beacon_thread = None
            print("beacon_thread stoped!")

        #server thread
        if self.server_thread != None:
            self.server_thread.stop()
            if(self.server_thread.is_alive()):
                self.server_thread.join()
                self.server_thread = None
            print("server_thread stoped!")

        #forwarding thread
        if self.forwarding_thread != None:
            self.forwarding_thread.stop()
            if(self.forwarding_thread.is_alive()):
                self.forwarding_thread.join()
                self.forwarding_thread = None
            print("forwarding_thread stoped!")

        #car subscriber thread
        if self.carSubscriber_thread != None:
            self.carSubscriber_thread.stop()
            if(self.carSubscriber_thread.is_alive()):
                self.carSubscriber_thread.join()
                self.carSubscriber_thread = None
            print("carSubscriber_thread stoped!")

    #================================ RUN THREADS =============================
    def run(self):
        while(self.runningThread):
            if (self.beacon_thread != None and not self.beacon_thread.is_alive()):
                print("Restart beacon thread")
                self.logFile.saveWithDate("Restart beacon thread")
                self.beacon_thread = ServerBeaconThread(
                            threadID         = self.threadID+1,
                            host_ip          = self.host_ip,
                            broadcast_ip     = self.broadcast_ip,
                            negotiation_port = self.negotiation_port,
                            sleepDuration    = 1.9,
                            logFile          = self.logFile
                        )
                self.beacon_thread.start()

            if (self.server_thread != None and not self.server_thread.is_alive()):
                print("Restart server thread")
                self.logFile.saveWithDate("Restart server thread")
                self.server_thread = ServerThread(
                            threadID = self.threadID+2,
                            address  = self.server_address.asTuple(),
                            carMap   = self.carMap,
                            logFile  = self.logFile
                        )
                self.server_thread.start()

            if (self.forwarding_thread != None and not self.forwarding_thread.is_alive()):
                print("Restart forwarding thread")
                self.logFile.saveWithDate("Restart forwarding thread")
                self.forwarding_thread = Forward2CarThread(
                            threadID    = self.threadID + 3,
                            car_communication_port = self.car_communication_port,
                            carMap      = self.carMap,
                            period      = 1.0,
                            logFile     = self.logFile
                        )
                self.forwarding_thread.start()

            if (self.carSubscriber_thread != None and not self.carSubscriber_thread.is_alive()):
                print("Restart carSubscriber thread")
                self.logFile.saveWithDate("Restart carSubscriber thread")
                self.carSubscriber_thread = Listen4CarSubscriberThread(
                            threadID    =  self.threadID + 4, 
                            host_ip     =  self.host_ip, 
                            car_subscription_port = self.car_subscription_port, 
                            carMap      =  self.carMap, 
                            logFile     =  self.logFile
                        )
                self.carSubscriber_thread.start()

            if(self.server_address.ip == '' and self.server_address.port == -1):
                self.NegotiateServer()
            time.sleep(1.1)

    #============================= STOP =======================================
    def stop(self):
        self.runningThread = False
   