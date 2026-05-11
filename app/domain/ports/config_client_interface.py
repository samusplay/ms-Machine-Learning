from abc import ABC, abstractmethod
from typing import Dict


#Firma ojo dene tener el mismo nombre 
class IConfigClient(ABC):
    @abstractmethod
    async def get_active_weights(self) -> Dict[str, float]:
        pass