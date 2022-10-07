from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime

class PriceDataInterface(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getPriceByIsin(isin: str, date: datetime): raise NotImplementedError

        
