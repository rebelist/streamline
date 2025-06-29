from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from pymongo import DESCENDING
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pytest_mock import MockerFixture

from streamline.domain.ticket import Ticket
from streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository
from streamline.infrastructure.mongo.ticket.repositories import MongoTicketRepository


class TestMongoTicketDocumentRepository:
    """Tests for the MongoTicketDocumentRepository class."""

    @pytest.fixture
    def mock_dependencies(self, mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
        """Fixture that sets up mocked database and collection."""
        mock_collection: MagicMock = mocker.MagicMock(spec=Collection)
        mock_database: MagicMock = mocker.MagicMock(spec=Database)
        mock_database.get_collection.return_value = mock_collection
        return mock_database, mock_collection

    def test_save_document(
        self,
        mock_dependencies: tuple[MagicMock, MagicMock],
    ) -> None:
        """Should delete and insert the ticket document correctly."""
        mock_database, mock_collection = mock_dependencies
        repository = MongoTicketDocumentRepository(mock_database)

        ticket_document: dict[str, Any] = {
            'id': 'TEST-115',
            'key': 'TEST-123',
            'team': 'Tito',
            'fields': {'summary': 'Some test ticket'},
            'changelog': {'histories': []},
        }

        repository.save(ticket_document)

        mock_database.get_collection.assert_called_once_with(MongoTicketDocumentRepository.COLLECTION_NAME)
        mock_collection.delete_one.assert_called_once_with({'id': 'TEST-115', 'team': 'Tito'})
        mock_collection.insert_one.assert_called_once_with(ticket_document)


class TestMongoTicketRepository:
    """Tests for the MongoTicketRepository class."""

    @pytest.fixture
    def mock_database(self, mocker: MockerFixture) -> Generator[MagicMock, None, None]:
        """Fixture that returns a mocked MongoDB database with a mocked collection."""
        mock_collection: MagicMock = mocker.Mock(spec=Collection)
        mock_db: MagicMock = mocker.Mock()
        mock_db.get_collection.return_value = mock_collection
        yield mock_db

    def test_find_by_team_name_returns_tickets(self, mock_database: MagicMock) -> None:
        """Should return a list of Ticket instances sorted by resolved_at when documents are found for the team."""
        mock_collection: MagicMock = mock_database.get_collection.return_value
        team_name: str = 'Team Alpha'
        mock_find_result = MagicMock()
        mock_collection.find.return_value = mock_find_result
        mock_sort_result = MagicMock()
        mock_find_result.sort.return_value = mock_sort_result

        mock_documents: list[dict[str, Any]] = [
            {
                'key': 'TICKET-1',
                'created_at': '2023-01-01T00:00:00Z',
                'started_at': '2023-01-02T00:00:00Z',
                'resolved_at': '2023-01-05T00:00:00Z',
                'team': team_name,
                'story_points': 1,
            },
            {
                'key': 'TICKET-2',
                'created_at': '2023-01-03T00:00:00Z',
                'started_at': '2023-01-04T00:00:00Z',
                'resolved_at': '2023-01-06T00:00:00Z',
                'team': team_name,
                'story_points': 2,
            },
        ]
        mock_sort_result.limit.return_value = mock_documents

        repo: MongoTicketRepository = MongoTicketRepository(mock_database)
        tickets: list[Ticket] = repo.find_by_team_name(team_name)

        assert len(tickets) == 2
        assert all(isinstance(ticket, Ticket) for ticket in tickets)
        assert tickets[0].id == 'TICKET-1'
        assert tickets[0].story_points == 1
        assert tickets[1].id == 'TICKET-2'
        assert tickets[1].story_points == 2
        mock_collection.find.assert_called_once_with({'team': team_name})
        mock_find_result.sort.assert_called_once_with('resolved_at', DESCENDING)
        mock_sort_result.limit.assert_called_once()

    def test_find_by_team_name_returns_empty_list(self, mock_database: MagicMock) -> None:
        """Should return an empty list when no documents are found for the team."""
        mock_collection: MagicMock = mock_database.get_collection.return_value
        mock_find_result = MagicMock()
        mock_collection.find.return_value = mock_find_result
        mock_find_result.sort.return_value.limit.return_value = []

        repo: MongoTicketRepository = MongoTicketRepository(mock_database)
        tickets: list[Ticket] = repo.find_by_team_name('GhostTeam')

        assert tickets == []
        mock_collection.find.assert_called_once_with({'team': 'GhostTeam'})
        mock_find_result.sort.assert_called_once_with('resolved_at', DESCENDING)
        mock_find_result.sort.return_value.limit.assert_called_once()
