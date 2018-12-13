import os
import sys
import math
import socket
import random
import threading

from cv2                import  aruco
from threading          import  Thread
from collections        import  namedtuple

from gps.Address                import *
from gps.ServerThreadManager    import *
from gps.SimulatorClient        import *

class SimulatedGps:
    ''' 
    This class implementing a simulated gps functionality based on Aruco 
    detection

    '''
    #================================ INIT ====================================
    def __init__(self):
        '''__init__ constructor
        '''

        self.logFile = logFile = ThreadSafeFileWriter('log.txt')

        (   bcast_ip,               host_ip,                negotiation_port, 
            subscription_port,      car_subscription_port,  car_com_port,   
            image_dimensions,       frame_rate,             image_brightness, 
            marker_width
        )                       =   SimulatedGps.init_parameters()
        
        self.server_address     =   Address("",0)

        self.simulatorClient = SimulatorClient(
                                    threadID        = 1,
                                    server_address  = self.server_address,
                                    logFile         = self.logFile
                                    )

        self.serverThreadManager = ServerThreadManager(
                            threadID                 = 2,
                            server_address           = self.server_address,
                            broadcast_ip             = bcast_ip,
                            host_ip                  = host_ip,
                            negotiation_port         = negotiation_port,
                            subscription_port        = subscription_port,
                            car_subscription_port    = car_subscription_port,
                            car_communication_port   = car_com_port,
                            max_wait_time_for_server = 10, 
                            logFile                  = self.logFile
                            )
    
    #================================ INIT PARAM ==============================
    def init_parameters():
        gw          =   os.popen("ip -4 route show default").read().split()
        s           =   socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2], 0))
        gateway     =   gw[2]
        HOST_NAME   =   socket.gethostname()
        HOST_IP     =   s.getsockname()[0]
        s.close()

        print ("IP:", HOST_IP, " GW:", gateway, " Host:", HOST_NAME)

        NEGOTIATION_PORT 	    = 12346
        SUBSCRITPION_PORT   	= NEGOTIATION_PORT + 1
        CAR_SUBSCRITPION_PORT 	= NEGOTIATION_PORT + 2
        CAR_COMMUNICATION_PORT  = CAR_SUBSCRITPION_PORT + 2
        BCAST_IP			    = '<broadcast>'#"172.24.1.255"
        IMAGE_DIMMENSIONS	    = (1648,1232) # (px,px)
        FRAME_RATE			    = 15 # fps
        IMAGE_BRIGHTNESS	    = 50 # %
        MARKER_WIDTH		    = 100 # mm      

        return  (BCAST_IP, HOST_IP, NEGOTIATION_PORT, SUBSCRITPION_PORT, 
                    CAR_SUBSCRITPION_PORT,CAR_COMMUNICATION_PORT,
                    IMAGE_DIMMENSIONS,FRAME_RATE,IMAGE_BRIGHTNESS,MARKER_WIDTH
            )

    #================================ RUN =====================================
    def run(self):
        try:
            self.logFile.open()
            try:
                self.serverThreadManager.NegotiateServer()
                self.serverThreadManager.start()
                self.simulatorClient.start()
                while(True):
                    s=0
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                pass

            self.simulatorClient.stop()
            self.simulatorClient.join()

            self.serverThreadManager.stop()
            self.serverThreadManager.join()

            self.serverThreadManager.stopAllThread()
            
            print("Active thread",threading.enumerate())
            self.logFile.close()

        except BaseException as e:
            print("[Exception Thrown] %s"%e)
        