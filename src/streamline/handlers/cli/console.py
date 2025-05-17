from typing import cast

import rich_click as click
from click import Command, Context

from streamline.config.container import Container
from streamline.handlers.cli.commands import database_clear, database_index, database_synchronize

container = Container.create()
settings = container.settings()


@click.group()
@click.version_option(settings.app.version, prog_name=settings.app.name)
@click.pass_context
def console(context: Context) -> None:
    """Provides commands for executing Streamline workflows and utilities."""
    context.obj = container


synchronizer: Command = cast(Command, database_synchronize)
clear: Command = cast(Command, database_clear)
index: Command = cast(Command, database_index)

console.container = container
console.add_command(index)
console.add_command(clear)
console.add_command(synchronizer)
