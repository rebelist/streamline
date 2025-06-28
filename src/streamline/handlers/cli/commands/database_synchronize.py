import rich_click as click
from click import Context

from streamline.application.ingestion.jobs.models import Executable
from streamline.handlers.cli.commands.command import Command, CommandTask


@click.command(name='database:synchronize')
@click.pass_context
def database_synchronize(context: Context) -> None:
    """Downloads data from different sources and saves it to the database."""
    container = context.obj

    command = Synchronizer()
    command.register(container.sprint_job())
    command.register(container.ticket_job())
    command.run()


class SyncTask:
    """Tasks to execute a synchronizer job."""

    def __init__(self, job: Executable) -> None:
        self.job = job
        self.description = str(job.__doc__)

    def execute(self) -> None:
        """Execute a job."""
        self.job.execute()


class Synchronizer(Command):
    """Orchestrates the data synchronization process using registered jobs."""

    def __init__(self) -> None:
        self.__jobs: list[Executable] = []

    def register(self, job: Executable) -> None:
        """Registers an executable job."""
        self.__jobs.append(job)

    def run(self) -> None:
        """Run command."""
        tasks: list[CommandTask] = [SyncTask(job) for job in self.__jobs]
        self._execute_tasks(tasks)
