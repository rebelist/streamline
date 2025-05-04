from typing import Any, Mapping

import rich_click as click
from click import Context
from pymongo.synchronous.database import Database

from streamline.handlers.cli.commands.command import Command


@click.command(name='database:clear')
@click.pass_context
def clear(context: Context) -> None:
    """Delete all database collections."""
    message = 'All data will be ' + click.style('deleted', fg='bright_magenta') + '. Are you sure you want to proceed?'
    container = context.obj

    if click.confirm(message):
        command = DatabaseEraser(container.database())
        command.run()
    else:
        click.echo('Bye!')


class DatabaseEraser(Command):
    """Truncate all collections."""

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__database = database

    def run(self) -> None:
        """Run command."""
        names = self.__database.list_collection_names()
        items = [self.__database[name] for name in names]
        Command._render_progress(
            lambda item: item.delete_many({}), lambda item: f'Deleting {item.name}...', items, 'Action'
        )
