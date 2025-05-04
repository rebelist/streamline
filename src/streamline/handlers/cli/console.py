from typing import cast

import rich_click as click
from click import Command, Context

from streamline.config.container import Container
from streamline.handlers.cli.commands import clear, synchronizer

container = Container.create()
settings = container.settings()


@click.group()
@click.version_option(settings.app.version, prog_name=settings.app.name)
@click.pass_context
def console(context: Context):
    """Provides commands for executing Streamline workflows and utilities."""
    context.obj = container


synchronizer: Command = cast(Command, synchronizer)
clear: Command = cast(Command, clear)

console.container = container
console.add_command(synchronizer)
console.add_command(clear)
