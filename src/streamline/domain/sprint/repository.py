from abc import ABC, abstractmethod

from streamline.domain.sprint.models import Sprint


class SprintRepository(ABC):
    """Sprint repository."""

    @abstractmethod
    def find_by_team_name(self, team: str) -> list[Sprint]:
        """Find sprints."""
        ...
