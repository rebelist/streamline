from typing import Any, Final, Mapping

from pymongo import DESCENDING
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from rebelist.streamline.domain.ticket import Ticket, TicketRepository


class MongoTicketDocumentRepository:
    """Ticket document ticket_repository to store raw jira ticket documents."""

    COLLECTION_NAME: Final[str] = 'jira_tickets'

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(self.COLLECTION_NAME)

    def save(self, ticket_document: Mapping[str, Any]) -> None:
        """Adds a jira ticket document."""
        self.__collection.delete_one({'id': ticket_document['id'], 'team': ticket_document['team']})
        self.__collection.insert_one(ticket_document)


class MongoTicketRepository(TicketRepository):
    """Ticket ticket_repository."""

    COLLECTION_NAME: Final[str] = 'jira_tickets'

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(self.COLLECTION_NAME)

    def find_by_team_name(self, team: str) -> list[Ticket]:
        """Returns all tickets of a team."""
        limit: Final[int] = 200
        documents = self.__collection.find({'team': team}).sort('resolved_at', DESCENDING).limit(limit)
        tickets: list[Ticket] = []

        for document in documents:
            ticket = Ticket(
                document['key'],
                document['created_at'],
                document['started_at'],
                document['resolved_at'],
                document['story_points'],
            )
            tickets.append(ticket)

        return tickets
