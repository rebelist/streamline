from typing import Any
from unittest.mock import MagicMock

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pytest_mock import MockerFixture

from streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


def test_mongo_ticket_document_repository_save(mocker: MockerFixture) -> None:
    """Test the MongoTicketDocumentRepository.save method."""
    mock_collection: MagicMock = mocker.MagicMock(spec=Collection)
    mock_database: MagicMock = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    repository: MongoTicketDocumentRepository = MongoTicketDocumentRepository(mock_database)
    ticket_document: dict[str, Any] = {
        'id': 'TEST-123',
        'key': 'TEST-123',
        'fields': {'summary': 'Some test ticket'},
        'changelog': {'histories': []},
    }
    repository.save(ticket_document)

    mock_database.get_collection.assert_called_once_with(MongoTicketDocumentRepository.COLLECTION_NAME)
    mock_collection.delete_one.assert_called_once_with({'id': 'TEST-123'})
    mock_collection.insert_one.assert_called_once_with(ticket_document)
