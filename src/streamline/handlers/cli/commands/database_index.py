from typing import Any, Mapping

import rich_click as click
from click import Context
from pymongo import ASCENDING
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from streamline.handlers.cli.commands.command import Command, CommandTask


@click.command(name='database:index')
@click.pass_context
def database_index(context: Context) -> None:
    """Create the streamline database."""
    container = context.obj
    command = DatabaseIndexer(container.database())
    command.run()


class IndexTask:
    """A task that creates indexes for a MongoDB collection."""

    def __init__(self, collection: Collection[Mapping[str, Any]]) -> None:
        """Initialize the task with a MongoDB collection."""
        self.collection: Collection[Mapping[str, Any]] = collection
        self.indexes: list[dict[str, Any]] = []
        self.description = f'Creating indexes for collection "{self.collection.name}"...'

    def add_index(self, keys: list[Any], unique: bool, name: str) -> None:
        """Add an index to be created on the collection."""
        self.indexes.append({'keys': keys, 'unique': unique, 'name': name})

    def execute(self) -> None:
        """Drop all existing indexes and create the configured ones on the collection."""
        self.collection.drop_indexes()
        for index in self.indexes:
            self.collection.create_index(index['keys'], unique=index['unique'], name=index['name'])


class DatabaseIndexer(Command):
    """CLI command to create indexes on selected collections in a MongoDB database."""

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        """Initialize the indexer with a MongoDB database."""
        self.__database = database

    def run(self) -> None:
        """Assemble and execute all index creation tasks."""
        tasks: list[CommandTask] = []

        task = IndexTask(self.__database['jobs'])
        task.add_index([('name', ASCENDING), ('team', ASCENDING)], True, 'jobs_name_team_unique_idx')
        tasks.append(task)

        task = IndexTask(self.__database['jira_sprints'])
        task.add_index([('id', ASCENDING), ('team', ASCENDING)], True, 'jira_sprints_id_team_unique_idx')
        task.add_index([('team', ASCENDING)], False, 'jira_sprints_team_idx')
        tasks.append(task)

        task = IndexTask(self.__database['jira_tickets'])
        task.add_index([('key', ASCENDING), ('team', ASCENDING)], True, 'jira_tickets_key_team_unique_idx')
        tasks.append(task)

        self._execute_tasks(tasks)
