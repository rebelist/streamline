from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Callable

from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TimeElapsedColumn
from rich.table import Table


class Command(ABC):
    """Abstract base class for commands."""

    @abstractmethod
    def run(self) -> None:
        """Runs the command."""
        ...

    @staticmethod
    def _init_progress() -> Progress:
        """Creates a progress bar for the command execution."""
        return Progress(BarColumn(), TimeElapsedColumn())

    @staticmethod
    def _render_progress(
        action: Callable[[Any], None], description: Callable[[Any], str], items: list[Any], title: str
    ) -> None:
        """Renders the command execution in the console."""
        progress = Progress(BarColumn(), TimeElapsedColumn())
        task = progress.add_task('', total=len(items) + 1)

        with Live(console=progress.console) as live:
            for item in items:
                summary = Panel(f'[yellow]{description(item)}', title=title)
                progress.update(task, advance=1)
                layout = Table.grid()
                layout.add_row(progress)
                layout.add_row(summary)
                live.update(layout)
                sleep(0.5)
                action(item)
            progress.update(task, advance=1)
