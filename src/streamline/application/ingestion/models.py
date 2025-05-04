from abc import ABC, abstractmethod


class Executable(ABC):
    """Executable job interface."""

    @abstractmethod
    def execute(self) -> None:
        """Executes as job."""
        ...
