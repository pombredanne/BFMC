from threading import Lock
from collections import namedtuple

data4CarStruct = namedtuple("data4CarStruct","IP DATA")

#================================ DATA CAR MAP ================================
class Data4CarMap:
    '''
        This class implementing a container for the vechiles
        This class is used for collecting the address and the data for each 
        vehicle client. 
        This container is thread safe, the modification of data 
        can't be interrupted by another
    '''

    #================================ INIT ====================================
    def __init__(self,size):
        '''Constructor
        
        Arguments:
            size {int} -- no of vehicles
        '''

        self.carMap     =   [data4CarStruct("","")] * size
        self.writelock  =   Lock()

    #================================ SET ITEM ================================
    def __setitem__(self,key,value):
        '''Setter
        
        Arguments:
            key {int}       -- the identification number of the vehicle
            value {tuple}   -- contains the ip address and the position
        '''
        with self.writelock:
            self.carMap[key] = value
    #================================ GETTER ==================================
    def __getitem__(self,key):
        '''Getter
        
        Arguments:
            key {int} -- the id number of the vehicle
        '''
        return self.carMap[key]
#==============================================================================