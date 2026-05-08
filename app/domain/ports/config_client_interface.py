from abc import ABC, abstractmethod
from typing import Dict


#Puerto Para traerse la configuracion
class IConfigClient(ABC):
    @abstractmethod
    def get_active_weights(self) -> Dict[str, float]:
        pass