import rich_click as click
from click import Context

from streamline.application.ingestion.models import Executable
from streamline.handlers.cli.commands.command import Command


@click.command(name='database:synchronize')
@click.pass_context
def synchronizer(context: Context) -> None:
    """Downloads data from different sources and saves it to the database."""
    container = context.obj

    command = Synchronizer()
    command.register(container.sprint_job())
    command.register(container.ticket_job())
    command.run()


class Synchronizer(Command):
    """Orchestrates the data synchronization process using registered jobs."""

    def __init__(self) -> None:
        self.__jobs: list[Executable] = []

    def register(self, job: Executable) -> None:
        """Registers an executable job."""
        self.__jobs.append(job)

    def run(self) -> None:
        """Run command."""
        Command._render_progress(lambda item: item.execute(), lambda item: item.__doc__, self.__jobs, 'Job')
