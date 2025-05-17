from typing import Any, Final, Mapping

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database


class MongoTicketDocumentRepository:
    """Ticket document repository to store raw jira ticket documents."""

    COLLECTION_NAME: Final[str] = 'jira_tickets'

    def __init__(self, database: Database[Mapping[str, Any]]) -> None:
        self.__collection: Collection[Mapping[str, Any]] = database.get_collection(
            MongoTicketDocumentRepository.COLLECTION_NAME
        )

    def save(self, ticket_document: Mapping[str, Any]) -> None:
        """Adds a jira ticket document."""
        self.__collection.delete_one({'id': ticket_document['id'], 'team': ticket_document['team']})
        self.__collection.insert_one(ticket_document)
