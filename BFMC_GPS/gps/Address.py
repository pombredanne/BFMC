#================================ ADDRESS CLS =================================
class Address:
    '''
        An address container
    '''

    def __init__(self,ip,port):
        self.ip     =   ip
        self.port   =   port

    def asTuple(self):
        return (self.ip,self.port)
