import abc

class ResponseMapper():
    def __init__(self):
        pass

    @abc.abstractmethod
    def map(self,response):
        pass
