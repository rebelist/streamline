from abc import ABC, abstractmethod
from typing import List

from streamline.domain.sprint.models import Sprint


class SprintRepository(ABC):
    """Sprint repository."""

    @abstractmethod
    def find_sprints(self) -> List[Sprint]:
        """Find sprints."""
        ...
