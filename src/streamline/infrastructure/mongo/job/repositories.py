from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final, Mapping, cast

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database


@dataclass
class Job:
    """Represents a data sync job."""

    name: str
    team: str
    executed_at: datetime | None = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=lambda: {})

    def to_dict(self) -> Mapping[str, Any]:
        """Serialize for MongoDB insertion/update."""
        return {
            'name': self.name,
            'team': self.team,
            'executed_at': self.executed_at,
            'metadata': self.metadata,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> Job | None:
        """Deserialize from MongoDB document."""
        return Job(
            name=cast(str, data.get('name')),
            team=cast(str, data.get('team')),
            executed_at=data.get('executed_at'),
            metadata=cast(dict[str, Any], data.get('metadata', {})),  # Provide default {}
        )


class JobRepository:
    """Sprint document ticket_repository to store raw jira sprint documents."""

    COLLECTION_NAME: Final[str] = 'jobs'

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(self.COLLECTION_NAME)

    def save(self, job: Job) -> None:
        """Saves a job."""
        self.__collection.delete_one({'team': job.team, 'name': job.name})
        self.__collection.insert_one(job.to_dict())

    def find(self, name: str, team: str) -> Job | None:
        """Find a job."""
        job: Job | None = None

        if name and team:
            document = self.__collection.find_one({'name': name, 'team': team})
            if document:
                job = Job.from_dict(document)

        return job
