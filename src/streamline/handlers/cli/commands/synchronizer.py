import rich_click as click


@click.command(name='synchronizer')
@click.option('--reset', default=False, help='Resets and synchronizes data by first deleting the existing data.')
def synchronizer(reset: bool) -> None:
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(f'Hello, {reset}!')
