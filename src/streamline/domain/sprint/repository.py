from abc import ABC, abstractmethod

from streamline.domain.sprint.models import Sprint


class SprintRepository(ABC):
    """Sprint ticket_repository."""

    @abstractmethod
    def find_by_team_name(self, team: str) -> list[Sprint]:
        """Find all sprints for a team."""
        ...
