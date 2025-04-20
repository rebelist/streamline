from typing import cast

import rich_click as click
from click import Command

from streamline.config import settings
from streamline.handlers.cli.commands import synchronizer


@click.group()
@click.version_option(settings.app.get('version'), prog_name=settings.app.get('name'))
def console():
    """Provides commands for executing Streamline workflows and utilities."""
    pass


synchronizer: Command = cast(Command, synchronizer)

console.add_command(synchronizer)
