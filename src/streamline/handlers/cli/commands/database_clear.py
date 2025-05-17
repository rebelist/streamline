from typing import Any, Mapping

import rich_click as click
from click import Context
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from streamline.handlers.cli.commands.command import Command, CommandTask


@click.command(name='database:clear')
@click.pass_context
def database_clear(context: Context) -> None:
    """Delete all database collections."""
    message = 'All data will be ' + click.style('deleted', fg='bright_magenta') + '. Are you sure you want to proceed?'
    container = context.obj

    if click.confirm(message):
        command = DatabaseEraser(container.database())
        command.run()
    else:
        click.echo('Bye!')


class ClearTask:
    """A task that creates indexes for a MongoDB collection."""

    collection: Collection[Mapping[str, Any]]

    def __init__(self, collection: Collection[Mapping[str, Any]]) -> None:
        """Initialize the task with a MongoDB collection."""
        self.collection = collection
        self.description = f'Clearing the collection "{self.collection.name}"...'

    def execute(self) -> None:
        """Delete all data in a collection."""
        self.collection.delete_many({})


class DatabaseEraser(Command):
    """Truncate all collections."""

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__database = database

    def run(self) -> None:
        """Run command."""
        names = self.__database.list_collection_names()
        tasks: list[CommandTask] = [ClearTask(self.__database[name]) for name in names]
        self._execute_tasks(tasks)
