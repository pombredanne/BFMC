#================================ CarClient ===================================
#  This module contains the logic for implementing the GPS
#  receiver of the car.
#
#  Functions for finding the  GPS server and for listening
#  for messages containing GPS localisation data are
#  implemented in this file.
#==============================================================================

import os
import sys
import socket 

from math       import  *
from random     import  *
from socket     import  *
from threading  import  Thread
from time       import  *

#================================ DISPLAY HOST DATA ===========================
gw = os.popen("ip -4 route show default").read().split()

s =	socket(AF_INET,SOCK_DGRAM)
s.connect((gw[2],0))

HOST_NAME =	gethostname()
HOST_IP	 = s.getsockname()[0]

s.close()

print("Host name:"+str(HOST_NAME)+" IP:"+str(HOST_IP))

#================================ PARAMETERS ==================================

THIS_CAR_ID 				= 2			# car marker ID attached to the car
MAX_WAIT_TIME_FOR_SERVER 	= 5

#communication parameters
SERVER_IP 					= None
NEGOTIATION_PORT    		= 12346
CAR_SUBSCRITPION_PORT   	= NEGOTIATION_PORT + 2
CAR_COMMUNICATION_PORT 		= CAR_SUBSCRITPION_PORT + 2

NEW_SERVER_IP				= False
car_id 						= THIS_CAR_ID

#flags
ID_SENT_FLAG				= False
START_UP					= True
G_Socket_Poz				= socket()
RUN_CARCLIENT				= True

#car related data
carOrientation 				= 0+0j
carPos 						= 0+0j

#================================ GET SERVER ==================================
def GetServer():
    '''
        Method used for listening the server IP. The Server can change.
    '''

    global SERVER_IP
    global NEGOTIATION_PORT
    global NEW_SERVER_IP
    global G_Socket_Poz
    global START_UP
    global ID_SENT_FLAG
    global RUN_CARCLIENT
    
    while RUN_CARCLIENT:
        try:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('', NEGOTIATION_PORT))
            s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            t 		= 	time()
            server 	= 	[]

            # Listen for server broadcast. 
            s.settimeout(MAX_WAIT_TIME_FOR_SERVER)

            # Receive data from the socket. Buffer size = 1500 bytes
            data, server_ip = s.recvfrom(1500, 0)

            # Get server IP                          
            if server_ip[0] != SERVER_IP:
                # new server
                SendIDToServer(server_ip[0])	
                NEW_SERVER_IP 	= 	True
                SERVER_IP 		= 	server_ip[0] # server is alive
                START_UP 		= 	False

            else:
                # old server
                if ID_SENT_FLAG == False:
                    SendIDToServer(server_ip[0])
                    print("Subscribe @ GPS server")
                NEW_SERVER_IP = False			
                # Server beacon received
                s.close()
            
        except Exception as e:
            SERVER_IP = None # Server is dead.
            if START_UP == False and SERVER_IP == None and NEW_SERVER_IP == True:
                G_Socket_Poz.close()
                G_Socket_Poz = None
                print("Socket from get position server closed!")
                
            print ("Not connected to server! IP: " + str(SERVER_IP) + 
                    "! Error:" + str(e)
                    )

            s.close()

#================================ SendIDtoServer ==============================
def SendIDToServer(new_server_ip):
    '''Send the car id to server for identification. 
    
    Arguments:
        new_server_ip {[type]} -- the ip of the new server
    '''

    global SERVER_IP
    global CAR_SUBSCRITPION_PORT
    global THIS_CAR_ID
    global ID_SENT_FLAG

    try:
        # Open connection to server.
        s = socket()         
        print("Vehicle " + str(THIS_CAR_ID) + 
                " subscribing to GPS server: " + str(new_server_ip) +
                ":"+ str(CAR_SUBSCRITPION_PORT)
            )

        s.connect((new_server_ip, CAR_SUBSCRITPION_PORT))
        sleep(2) 
        car_id_str = str(THIS_CAR_ID)
        s.send(bytes(car_id_str, "UTF-8"))
        # Shut down conn. Further sends are disallowed.
        s.shutdown(SHUT_WR)
        s.close()
        print("Vehicle ID sent to server----------------------------")
        ID_SENT_FLAG = True

    except Exception as e:
        print("Failed to send ID to server, with error: " + str(e))
        s.close()
        ID_SENT_FLAG = False

#================================ GET DATA ====================================
def GetPositionDataFromServer_Thread():
    '''
    Utility function for receiving the car position and orientation from the server.
    '''

    global car_id
    global carPos
    global carOrientation
    global SERVER_IP
    global NEW_SERVER_IP
    global THIS_CAR_ID
    global CAR_COMMUNICATION_PORT
    global G_Socket_Poz
    global RUN_CARCLIENT

    while RUN_CARCLIENT:
        if SERVER_IP != None:	# If server alive/valid
            if NEW_SERVER_IP == True:
                try:
                    G_Socket_Poz.close()
                    G_Socket_Poz=None
                except:
                    # Do nothing.
                    print("Previous socket cound not be closed.")
            if G_Socket_Poz==None:
                # Server changed.
                try:
                    # If there is a GPS server available then open a socket and then wait for GPS data.
                    print("Attempting to create new socket to receive the position from server "+str(HOST_IP)+":"+str(CAR_COMMUNICATION_PORT))
                    #G_Socket_Poz = socket()   		
                    G_Socket_Poz = socket(AF_INET, SOCK_STREAM)
                    # Set socket flag socket.SO_REUSEADDR for preventing "[Errno 98] Address already in use" error
                    # when restarting application 
                    G_Socket_Poz.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                    G_Socket_Poz.bind((HOST_IP, CAR_COMMUNICATION_PORT))      
                    G_Socket_Poz.listen(2)

                    NEW_SERVER_IP = False	
                
                except Exception as e:
                    print("Creating new socket for get position from server " + str(SERVER_IP) + " failed with error: "+str(e))
                    sleep(1)
                    G_Socket_Poz = None		
            
            if not G_Socket_Poz == None:
                # Server did not change.
                try:
                    c, addr = 	G_Socket_Poz.accept()
                    # raw message   
                    data 	= 	str(c.recv(4096))   
                    # mesage parsing
                    car_id  = 	int(data.split(';')[0].split(':')[1])
                    
                    if car_id == THIS_CAR_ID:
                        # Compute car position.
                        carPos = complex(float(data.split(';')[1].split(':')[1].split('(')[1].split('+')[0]), float(data.split(';')[1].split(':')[1].split('j')[0].split('+')[1]))
                        # Compute car orientation.
                        carOrientation = complex(float(data.split(';')[2].split(':')[1].split('(')[1].split('+')[0]), float(data.split(';')[2].split(':')[1].split('j')[0].split('+')[1]))
                        
                        print("id:" + str(car_id) + " -position: " + str(carPos) + " -orientation: " + str(carOrientation))
                    c.close()

                except Exception as e:
                        print("Receiving position data from server " + str(SERVER_IP) + " failed with error: " + str(e))
                        c.close()
    
#================================ MAIN ========================================
def main():
    global RUN_CARCLIENT
    print("First start up of vehicle client ...")

    # thread responsible for subscribing to GPS server
    connection_thread = Thread(target = GetServer)

    # thread responsible for receiving GPS data from server
    position_thread = Thread(target = GetPositionDataFromServer_Thread)
    
    try:
        # start all threads
        connection_thread.start()
        position_thread.start()
        while RUN_CARCLIENT:
            print("Running")
            sleep(30)
    except KeyboardInterrupt as e:
        RUN_CARCLIENT=False
        try:
            global G_Socket_Poz
            G_Socket_Poz.close()
            print("\nClient socket closed!")
        
        except:
            print("Cannot close client socket!")
            pass
        
        print("KeyboardInterrupt!!")
        pass

##  Set execution entry point.
if __name__ == "__main__":
    main()