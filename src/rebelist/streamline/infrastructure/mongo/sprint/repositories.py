from typing import Any, Final, Mapping

from pymongo import ASCENDING, DESCENDING
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from rebelist.streamline.domain.sprint import Sprint, SprintRepository
from rebelist.streamline.domain.ticket import Ticket
from rebelist.streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


class MongoSprintRepository(SprintRepository):
    """Sprint ticket_repository."""

    COLLECTION_NAME: Final[str] = 'jira_sprints'
    LIMIT_SPRINTS: Final[int] = 20

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(
            MongoSprintRepository.COLLECTION_NAME
        )

    def find_by_team_name(self, team: str) -> list[Sprint]:
        """Returns all sprints with its tickets."""
        sprints: list[Sprint] = []
        pipeline = [
            {
                '$lookup': {
                    'from': MongoTicketDocumentRepository.COLLECTION_NAME,
                    'localField': 'tickets',
                    'foreignField': 'key',
                    'as': 'issues',
                }
            },
            {'$match': {'issues': {'$elemMatch': {'team': team}}}},
            {
                '$project': {
                    'name': True,
                    'opened_at': True,
                    'closed_at': True,
                    'issues.key': True,
                    'issues.story_points': True,
                    'issues.created_at': True,
                    'issues.started_at': True,
                    'issues.resolved_at': True,
                }
            },
            {'$sort': {'closed_at': DESCENDING}},
            {'$limit': MongoSprintRepository.LIMIT_SPRINTS},
            {'$sort': {'closed_at': ASCENDING}},
        ]
        documents = self.__collection.aggregate(pipeline)

        for document in documents:
            tickets: list[Ticket] = []
            for issue in document['issues']:
                ticket = Ticket(
                    issue['key'], issue['created_at'], issue['started_at'], issue['resolved_at'], issue['story_points']
                )
                tickets.append(ticket)

            sprint = Sprint(document['name'], document['opened_at'], document['closed_at'], tickets)
            sprints.append(sprint)

        return sprints


class MongoSprintDocumentRepository:
    """Sprint document ticket_repository to store raw jira sprint documents."""

    COLLECTION_NAME: Final[str] = 'jira_sprints'

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(self.COLLECTION_NAME)

    def save(self, sprint_document: Mapping[str, Any]) -> None:
        """Adds a jira sprint document."""
        self.__collection.delete_one({'id': sprint_document['id'], 'team': sprint_document['team']})
        self.__collection.insert_one(sprint_document)
