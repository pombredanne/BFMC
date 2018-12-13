import time
import socket

from threading import Thread
#================================ SERVER BEACON THREAD ========================
class ServerBeaconThread(Thread):
    '''ServerBeaconThread 
    
        This class is implementing a thread with a broadcast functionality
        Periodically signalling itself as the server.
    
    '''

    #================================ INIT ====================================
    def __init__(self, threadID, host_ip, broadcast_ip, negotiation_port,
                    sleepDuration, logFile = None
                ):
        '''__initConstructor
        
        Arguments:
            threadID {int}          -- the id of the thread
            host_ip {str}           -- the host ip
            broadcast_ip {str}      -- the broadcast i[]
            negotiation_port {int}  -- port number for the beacon
            sleepDuration {float}   -- duration between two transmiting 
        
        Keyword Arguments:
            logFile {str}           -- (default: {None})
        '''

        Thread.__init__(self)
        self.name               = 'ServerBeaconThread'
        self.threadID           = threadID
        self.sleepDuration      = sleepDuration
        self.negotiation_port   = negotiation_port
        self.host_ip            = host_ip
        self.broadcast_ip       = broadcast_ip
        self.runningThread      = True
        self.logFile            = logFile

    #================================ RUN =====================================
    def run(self):
        '''run thread
        '''

        try:
            beacon = socket.socket(
                            family  = socket.AF_INET,
                            type    =  socket.SOCK_DGRAM
                        )

            beacon.bind(('', self.negotiation_port))

            beacon.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            if(self.logFile != None):			
                self.logFile.saveWithDate(self.name+' started')
            
            #send data while thread is running
            while self.runningThread:
                beacon.sendto(
                            bytes(self.host_ip, "UTF-8"), 
                            (self.broadcast_ip, self.negotiation_port)
                            )
                time.sleep(self.sleepDuration)
            beacon.close()

            #save file is stopped
            if(self.logFile != None):			
                self.logFile.saveWithDate(self.name+' stoped')

        except BaseException as e:
            self.runningThread = False
            if(self.logFile != None):			
                self.logFile.saveWithDate(self.name + ' stoped with exception ' + str(e) )
    
    #================================ STOP THREAD =============================
    def stop(self):
        self.runningThread = False
#==============================================================================
