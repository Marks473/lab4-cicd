from abc import ABC, abstractmethod
from typing import List, Optional

from converter.domain.entities import ConversionTaskEntity


class ConversionTaskRepository(ABC):
    @abstractmethod
    def list_all(self, filters=None) -> List[ConversionTaskEntity]:
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[ConversionTaskEntity]:
        pass

    @abstractmethod
    def create(self, task: ConversionTaskEntity) -> ConversionTaskEntity:
        pass

    @abstractmethod
    def update(self, task: ConversionTaskEntity) -> ConversionTaskEntity:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> None:
        pass