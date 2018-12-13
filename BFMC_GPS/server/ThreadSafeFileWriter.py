import os
import sys
import time
import socket
import datetime

from threading import Lock

#================================ THREAD SAFE FILE WRITER =====================
class ThreadSafeFileWriter:
    '''
        This class implementing a thread safe file writer
    '''
    
    #================================ INIT ====================================
    def __init__(self,fileName):
        '''Constructor
        
        Arguments:
            fileName {string} -- the name of the file
        '''
        self.fileName   =   fileName
        self.file       =   None
        self.writeLock  =   Lock()

    #================================ OPEN ====================================
    def open(self):
        '''
            Open a file
        '''
        try:
            self.file = os.open(self.fileName,os.O_RDWR|os.O_CREAT|os.O_SYNC|os.O_TRUNC)
            return True

        except BaseException as e:
            print("[Exception Thrown] %s"%e)
            pass

        return False

    #================================ CLOSE ===================================
    def close(self):
        '''Close

        '''
        if (self.file != None):
            os.close(self.file)
            self.file = None
            return True
        
        return False

    #================================ SAVE W/ DATE ============================
    def saveWithDate(self,str_txt):
        '''SaveWithDate
        
        Arguments:
            str_txt {string} -- the text to be written into the file
        '''

        ts = time.time()
        timestamp_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        return self.save(timestamp_str + " - " + str_txt + '\n')

    #================================ SAVE ====================================
    def save(self,str_txt):
        '''Save the message into the folder
        
        Arguments:
            str_txt {string} -- the text to be saved
        '''

        if (self.file!=None):
            os.write(self.file,str_txt.encode('ascii'))
            return True
            
        return False
#==============================================================================
 