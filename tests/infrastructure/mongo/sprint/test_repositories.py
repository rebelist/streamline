from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pytest_mock import MockerFixture

from rebelist.streamline.domain.sprint import Sprint
from rebelist.streamline.domain.ticket import Ticket
from rebelist.streamline.infrastructure.mongo.sprint import MongoSprintDocumentRepository, MongoSprintRepository
from rebelist.streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


def test_mongo_sprint_repository_find_by_team_name(mocker: MockerFixture) -> None:
    """Test the MongoSprintRepository.find_by_team_name method."""
    mock_collection: MagicMock = mocker.MagicMock(spec=Collection)
    mock_database: MagicMock = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    mock_aggregate_result = [
        {
            '_id': {'$oid': '64567890abcdef1234567890'},
            'name': 'Sprint 1',
            'opened_at': datetime(2025, 5, 1, 0, 0),
            'closed_at': datetime(2025, 5, 15, 0, 0),
            'issues': [
                {
                    'key': 'TEST-1',
                    'created_at': datetime(2025, 4, 2, 9, 0),
                    'started_at': datetime(2025, 5, 2, 9, 0),
                    'resolved_at': datetime(2025, 5, 14, 17, 0),
                    'story_points': 1,
                },
                {
                    'key': 'TEST-2',
                    'created_at': datetime(2025, 3, 2, 9, 0),
                    'started_at': datetime(2025, 5, 3, 10, 0),
                    'resolved_at': datetime(2025, 5, 13, 16, 0),
                    'story_points': 1,
                },
            ],
        },
        {
            '_id': {'$oid': '64567890abcdef1234567891'},
            'name': 'Sprint 2',
            'opened_at': datetime(2025, 5, 16, 0, 0),
            'closed_at': datetime(2025, 5, 30, 0, 0),
            'issues': [
                {
                    'key': 'TEST-3',
                    'created_at': datetime(2025, 3, 17, 11, 0),
                    'started_at': datetime(2025, 5, 17, 11, 0),
                    'resolved_at': datetime(2025, 5, 29, 18, 0),
                    'story_points': 1,
                },
            ],
        },
    ]
    mock_collection.aggregate.return_value = mock_aggregate_result

    repository: MongoSprintRepository = MongoSprintRepository(mock_database)
    sprints: list[Sprint] = repository.find_by_team_name('TestTeam')

    mock_database.get_collection.assert_called_once_with(MongoSprintRepository.COLLECTION_NAME)
    mock_collection.aggregate.assert_called_once()
    pipeline_arg = mock_collection.aggregate.call_args[0][0]
    assert pipeline_arg[0]['$lookup']['from'] == MongoTicketDocumentRepository.COLLECTION_NAME
    assert len(sprints) == 2

    sprint1 = sprints[0]
    assert sprint1.name == 'Sprint 1'
    assert sprint1.opened_at == datetime(2025, 5, 1, 0, 0)
    assert sprint1.closed_at == datetime(2025, 5, 15, 0, 0)
    assert len(sprint1.tickets) == 2
    assert sprint1.tickets[0] == Ticket(
        'TEST-1', datetime(2025, 4, 2, 9, 0), datetime(2025, 5, 2, 9, 0), datetime(2025, 5, 14, 17, 0), 1
    )
    assert sprint1.tickets[1] == Ticket(
        'TEST-2', datetime(2025, 3, 2, 9, 0), datetime(2025, 5, 3, 10, 0), datetime(2025, 5, 13, 16, 0), 1
    )

    sprint2 = sprints[1]
    assert sprint2.name == 'Sprint 2'
    assert sprint2.opened_at == datetime(2025, 5, 16, 0, 0)
    assert sprint2.closed_at == datetime(2025, 5, 30, 0, 0)
    assert len(sprint2.tickets) == 1
    assert sprint2.tickets[0] == Ticket(
        'TEST-3', datetime(2025, 3, 17, 11, 0), datetime(2025, 5, 17, 11, 0), datetime(2025, 5, 29, 18, 0), 1
    )


def test_mongo_sprint_document_repository_save(mocker: MockerFixture) -> None:
    """Test the MongoSprintDocumentRepository.save method."""
    mock_collection: MagicMock = mocker.MagicMock(spec=Collection)
    mock_database: MagicMock = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    repository: MongoSprintDocumentRepository = MongoSprintDocumentRepository(mock_database)
    sprint_document: dict[str, Any] = {
        'id': 123,
        'name': 'Sprint X',
        'team': 'Bimbo',
        'startDate': '2025-05-08T00:00:00.000+0000',
        'completeDate': '2025-05-22T00:00:00.000+0000',
        'tickets': ['KEY-101', 'KEY-102'],
    }
    repository.save(sprint_document)

    mock_database.get_collection.assert_called_once_with(MongoSprintDocumentRepository.COLLECTION_NAME)
    mock_collection.delete_one.assert_called_once_with({'id': 123, 'team': 'Bimbo'})
    mock_collection.insert_one.assert_called_once_with(sprint_document)
