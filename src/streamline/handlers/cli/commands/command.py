from abc import ABC, abstractmethod
from time import sleep
from typing import Protocol, runtime_checkable

from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TimeElapsedColumn
from rich.table import Table


@runtime_checkable
class CommandTask(Protocol):
    """Command task protocol to execute with a progress bar."""

    description: str

    def execute(self) -> None:
        """Execute as task."""
        ...


class Command(ABC):
    """Abstract base class for commands."""

    @abstractmethod
    def run(self) -> None:
        """Runs the command."""
        ...

    @staticmethod
    def _execute_tasks(tasks: list[CommandTask]) -> None:
        """Execute tasks."""
        progress = Progress(BarColumn(), TimeElapsedColumn())
        rich_task = progress.add_task('', total=len(tasks) + 1)

        with Live(console=progress.console) as live:
            for task in tasks:
                summary = Panel(f'[yellow]{task.description}', title='Action')
                progress.update(rich_task, advance=1)
                layout = Table.grid()
                layout.add_row(progress)
                layout.add_row(summary)
                live.update(layout)
                sleep(0.5)
                task.execute()
            progress.update(rich_task, advance=1)
