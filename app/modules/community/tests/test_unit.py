import pytest
from app.modules.community.models import CommunityType, UserRole
from app.modules.community.services import CommunityService
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


@pytest.fixture
def community_service():
    return CommunityService()


def test_get_all(community_service):
    with patch.object(community_service.repository, 'get_all') as mock_get_all:
        mock_get_all.return_value = ['community1', 'community2']
        result = community_service.get_all()
        assert result == ['community1', 'community2']
        mock_get_all.assert_called_once()


def test_is_user_community_member(community_service):
    with patch.object(
        community_service.user_community_repository,
        'is_user_member_of_community'
    ) as mock_is_user_member_of_community:
        user_id = 1
        community_id = 100

        mock_is_user_member_of_community.return_value = True
        result = community_service.is_user_community_member(user_id, community_id)
        assert result is True
        mock_is_user_member_of_community.assert_called_once_with(user_id, community_id)

        mock_is_user_member_of_community.return_value = False
        result = community_service.is_user_community_member(user_id, community_id)
        assert result is False
        mock_is_user_member_of_community.assert_called_with(user_id, community_id)


def test_get_user_communities(community_service):
    with patch.object(community_service.user_community_repository, 'get_user_communities') as mock_get_user_communities:
        user_id = 1
        mock_user = MagicMock(id=user_id)

        mock_communities = [MagicMock(id=101), MagicMock(id=102)]
        mock_get_user_communities.return_value = mock_communities
        result = community_service.get_user_communities(mock_user)

        assert result == mock_communities
        assert len(result) == 2
        mock_get_user_communities.assert_called_once_with(user_id)


def test_is_user_community_creator(community_service):
    with patch.object(community_service.user_community_repository, 'get_user_community') as mock_get_user_community:
        user_id = 1
        community_id = 100

        mock_association = MagicMock(role=UserRole.CREATOR)
        mock_get_user_community.return_value = mock_association
        result = community_service.is_user_community_creator(user_id, community_id)
        assert result is True
        mock_get_user_community.assert_called_once_with(user_id, community_id)
        mock_get_user_community.reset_mock()

        mock_get_user_community.return_value = None
        result = community_service.is_user_community_creator(user_id, community_id)
        assert result is False
        mock_get_user_community.assert_called_once_with(user_id, community_id)
        mock_get_user_community.reset_mock()

        mock_get_user_community.return_value = MagicMock(role=UserRole.ADMIN)
        result = community_service.is_user_community_creator(user_id, community_id)
        assert result is False
        mock_get_user_community.assert_called_once_with(user_id, community_id)


def test_is_user_community_admin(community_service):
    with patch.object(community_service.user_community_repository, 'get_user_community') as mock_get_user_community:
        user_id = 1
        community_id = 100

        mock_association = MagicMock(role=UserRole.ADMIN)
        mock_get_user_community.return_value = mock_association
        result = community_service.is_user_community_admin(user_id, community_id)
        assert result is True
        mock_get_user_community.assert_called_once_with(user_id, community_id)
        mock_get_user_community.reset_mock()

        mock_get_user_community.return_value = None
        result = community_service.is_user_community_admin(user_id, community_id)
        assert result is False
        mock_get_user_community.assert_called_once_with(user_id, community_id)
        mock_get_user_community.reset_mock()

        mock_get_user_community.return_value = MagicMock(role=UserRole.CREATOR)
        result = community_service.is_user_community_admin(user_id, community_id)
        assert result is False
        mock_get_user_community.assert_called_once_with(user_id, community_id)


def test_edit_community(community_service):
    user_id = 1
    community_id = 100
    user = MagicMock(id=user_id)
    form = MagicMock()
    form.data = {'name': 'Updated Community', 'description': 'Updated Description'}

    with patch.object(community_service, 'is_user_community_creator', return_value=False) as mock_is_creator:
        result, message = community_service.edit_community(user, community_id, form)
        assert result is False
        assert message == 'Only the creator can edit this community.'
        mock_is_creator.assert_called_once_with(user_id, community_id)

    with patch.object(community_service, 'is_user_community_creator', return_value=True) as mock_is_creator, \
         patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(community_service, 'update') as mock_update:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.edit_community(user, community_id, form)

        assert result is True
        assert message == 'Community updated successfully.'
        mock_is_creator.assert_called_with(user_id, community_id)
        mock_get_community.assert_called_once_with(community_id)
        mock_update.assert_called_once_with(community_id, **form.data)

    with patch.object(community_service, 'is_user_community_creator', return_value=True) as mock_is_creator, \
         patch.object(community_service.repository, 'get_community_by_id', return_value=None) as mock_get_community:

        result, message = community_service.edit_community(user, community_id, form)

        assert result is False
        assert message == 'Community not found.'
        mock_is_creator.assert_called_with(user_id, community_id)
        mock_get_community.assert_called_once_with(community_id)


def test_delete_community(community_service):
    user_id = 1
    community_id = 100
    user = MagicMock(id=user_id)

    with patch.object(community_service, 'is_user_community_creator', return_value=False) as mock_is_creator:
        result, message = community_service.delete_community(user, community_id)
        assert result is False
        assert message == 'Only the community creator can delete this community.'
        mock_is_creator.assert_called_once_with(user_id, community_id)

    with patch.object(community_service, 'is_user_community_creator', return_value=True) as mock_is_creator, \
         patch.object(community_service.user_community_repository, 'delete_all_by_community_id') as mock_delete_all, \
         patch.object(community_service.repository, 'delete') as mock_delete:

        result, message = community_service.delete_community(user, community_id)

        assert result is True
        assert message == 'Community and all associated members have been deleted.'
        mock_is_creator.assert_called_with(user_id, community_id)
        mock_delete_all.assert_called_once_with(community_id)
        mock_delete.assert_called_once_with(community_id)

    with patch.object(community_service, 'is_user_community_creator', return_value=True) as mock_is_creator, \
         patch.object(
             community_service.user_community_repository,
             'delete_all_by_community_id',
             side_effect=Exception("Deletion error")
         ) as mock_delete_all, patch.object(community_service.repository, 'delete') as mock_delete:

        result, message = community_service.delete_community(user, community_id)

        assert result is False
        assert message == 'An error occurred while deleting the community: Deletion error'
        mock_is_creator.assert_called_with(user_id, community_id)
        mock_delete_all.assert_called_once_with(community_id)
        mock_delete.assert_not_called()


def test_join_community(community_service):
    user_id = 1
    community_id = 100
    user = MagicMock(id=user_id)

    with patch.object(
            community_service.repository, 'get_community_by_id', return_value=None
    ) as mock_get_community:
        result, message = community_service.join_community(user, community_id)
        assert result is False
        assert message == 'Community does not exist.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=True
         ) as mock_is_member:

        mock_get_community.return_value = MagicMock(id=community_id, name="Test Community")
        result, message = community_service.join_community(user, community_id)

        assert result is False
        assert message == 'You are already a member of this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
         ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
         ) as mock_is_member, \
        patch.object(
            community_service.user_community_repository,
            'add_user_to_community'
         ) as mock_add_user:

        mock_community = MagicMock(id=community_id, name="Test Community")
        mock_community.name = "Test Community"
        mock_get_community.return_value = mock_community
        result, message = community_service.join_community(user, community_id)

        assert result is True
        assert message == 'You have successfully joined the community: Test Community'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_add_user.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
         ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
         ) as mock_is_member, \
        patch.object(
            community_service.user_community_repository,
            'add_user_to_community',
            side_effect=Exception("Join error")
         ) as mock_add_user:

        mock_community = MagicMock(id=community_id, name="Test Community")
        mock_get_community.return_value = mock_community
        result, message = community_service.join_community(user, community_id)

        assert result is False
        assert message == 'An error occurred while trying to join the community. Please try again: Join error'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_add_user.assert_called_once_with(user_id, community_id)


def test_leave_community(community_service):
    user_id = 1
    community_id = 100
    user = MagicMock(id=user_id)

    with patch.object(community_service.repository, 'get_community_by_id', return_value=None) as mock_get_community:
        result, message = community_service.leave_community(user, community_id)
        assert result is False
        assert message == 'Community does not exist.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(
             community_service.user_community_repository,
             'is_user_member_of_community',
             return_value=False
         ) as mock_is_member:

        mock_get_community.return_value = MagicMock(id=community_id, name="Test Community")
        result, message = community_service.leave_community(user, community_id)

        assert result is False
        assert message == 'You are not a member of this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
             community_service.user_community_repository,
             'is_user_member_of_community',
             return_value=True
         ) as mock_is_member, \
        patch.object(
             community_service,
             'is_user_community_creator',
             return_value=True
         ) as mock_is_creator:

        mock_get_community.return_value = MagicMock(id=community_id, name="Test Community")
        result, message = community_service.leave_community(user, community_id)

        assert result is False
        assert message == 'You cannot leave a community you created.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_creator.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
             community_service.user_community_repository,
             'is_user_member_of_community',
             return_value=True
         ) as mock_is_member, \
        patch.object(
             community_service,
             'is_user_community_creator',
             return_value=False
         ) as mock_is_creator, \
        patch.object(
             community_service.user_community_repository,
             'delete'
         ) as mock_delete:

        mock_community = MagicMock(id=community_id)
        mock_community.name = "Test Community"
        mock_get_community.return_value = mock_community
        result, message = community_service.leave_community(user, community_id)

        assert result is True
        assert message == 'You have successfully left the community: Test Community'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_creator.assert_called_once_with(user_id, community_id)
        mock_delete.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
         ) as mock_get_community, \
        patch.object(
             community_service.user_community_repository,
             'is_user_member_of_community',
             return_value=True
         ) as mock_is_member, \
        patch.object(
             community_service,
             'is_user_community_creator',
             return_value=False
         ) as mock_is_creator, \
        patch.object(
             community_service.user_community_repository,
             'delete',
             side_effect=Exception("Leave error")
         ) as mock_delete:

        mock_community = MagicMock(id=community_id)
        mock_community.name = "Test Community"
        mock_get_community.return_value = mock_community
        result, message = community_service.leave_community(user, community_id)

        assert result is False
        assert message == 'An error occurred while trying to leave the community. Please try again: Leave error'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_creator.assert_called_once_with(user_id, community_id)
        mock_delete.assert_called_once_with(user_id, community_id)


def test_create_community(community_service):
    user_id = 1
    user = MagicMock(id=user_id)
    community_name = "New Community"
    community_type = CommunityType.PUBLIC
    community_description = "A test community"

    with patch.object(community_service.repository, 'create') as mock_create, \
         patch.object(
            community_service.user_community_repository,
            'add_user_to_community'
         ) as mock_add_user:

        mock_community = MagicMock(id=100, name=community_name)
        mock_create.return_value = mock_community

        result, message = community_service.create_community(
            user=user,
            name=community_name,
            type=community_type,
            description=community_description
        )

        assert result is True
        assert message == f'Community "{community_name}" created successfully.'
        mock_create.assert_called_once_with(
            name=community_name,
            type=community_type,
            description=community_description
        )
        mock_add_user.assert_called_once_with(
            user_id=user_id,
            community_id=mock_community.id,
            role=UserRole.CREATOR
        )

    with patch.object(community_service.repository, 'create') as mock_create, \
         patch.object(
            community_service.user_community_repository,
            'add_user_to_community',
            side_effect=Exception("Creation error")
         ) as mock_add_user:

        mock_community = MagicMock(id=101, name=community_name)
        mock_create.return_value = mock_community

        result, message = community_service.create_community(
            user=user,
            name=community_name,
            type=community_type,
            description=community_description
        )

        assert result is False
        assert message == 'An error occurred while creating the community: Creation error'
        mock_create.assert_called_once_with(
            name=community_name,
            type=community_type,
            description=community_description
        )
        mock_add_user.assert_called_once_with(
            user_id=user_id,
            community_id=mock_community.id,
            role=UserRole.CREATOR
        )


def test_request_join_community(community_service):
    user_id = 1
    community_id = 100
    user = MagicMock(id=user_id)
    community_name = "Private Community"

    with patch.object(community_service.repository, 'get_community_by_id', return_value=None) as mock_get_community:
        result, message = community_service.request_join_community(user, community_id)
        assert result is False
        assert message == 'Community does not exist.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community:
        mock_community = MagicMock(id=community_id, type=CommunityType.PUBLIC, name=community_name)
        mock_get_community.return_value = mock_community
        result, message = community_service.request_join_community(user, community_id)

        assert result is False
        assert message == 'Requests can only be made to private communities.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=True
         ) as mock_is_member:

        mock_community = MagicMock(id=community_id, type=CommunityType.PRIVATE, name=community_name)
        mock_get_community.return_value = mock_community
        result, message = community_service.request_join_community(user, community_id)

        assert result is False
        assert message == 'You are already a member of this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
         ) as mock_is_member, \
        patch.object(
            community_service.join_request_repository,
            'is_request_already_made',
            return_value=True
         ) as mock_is_request_made:

        mock_community = MagicMock(id=community_id, type=CommunityType.PRIVATE, name=community_name)
        mock_get_community.return_value = mock_community
        result, message = community_service.request_join_community(user, community_id)

        assert result is False
        assert message == 'You have already requested to join this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_request_made.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
         ) as mock_is_member, \
        patch.object(
            community_service.join_request_repository,
            'is_request_already_made',
            return_value=False
         ) as mock_is_request_made, \
        patch.object(
            community_service.join_request_repository,
            'create'
         ) as mock_create_request:

        mock_community = MagicMock(id=community_id, type=CommunityType.PRIVATE)
        mock_community.name = community_name
        mock_get_community.return_value = mock_community
        result, message = community_service.request_join_community(user, community_id)

        assert result is True
        assert message == f'Request to join {community_name} successfully sent.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_request_made.assert_called_once_with(user_id, community_id)
        mock_create_request.assert_called_once_with(user_id=user.id, community_id=community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
        ) as mock_is_member, \
        patch.object(
            community_service.join_request_repository,
            'is_request_already_made',
            return_value=False
        ) as mock_is_request_made, \
        patch.object(
            community_service.join_request_repository,
            'create',
            side_effect=Exception("Request error")
         ) as mock_create_request:

        mock_community = MagicMock(id=community_id, type=CommunityType.PRIVATE, name=community_name)
        mock_get_community.return_value = mock_community
        result, message = community_service.request_join_community(user, community_id)

        assert result is False
        assert message == 'An error occurred while trying to request to join community. Please try again: Request error'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(user_id, community_id)
        mock_is_request_made.assert_called_once_with(user_id, community_id)
        mock_create_request.assert_called_once_with(user_id=user.id, community_id=community_id)


def test_accept_join_request(community_service):
    user_id = 1
    request_id = 200
    community_id = 100
    join_request_user_id = 2
    user = MagicMock(id=user_id)

    with patch.object(
            community_service.join_request_repository,
            'get_request_by_id',
            return_value=None
         ) as mock_get_request:
        result, message = community_service.accept_join_request(user, request_id)
        assert result is False
        assert message == 'Join request does not exist.'
        mock_get_request.assert_called_once_with(request_id)

    with patch.object(
            community_service.join_request_repository,
            'get_request_by_id'
        ) as mock_get_request, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=False
        ) as mock_is_admin, \
        patch.object(
            community_service,
            'is_user_community_creator',
            return_value=False
         ) as mock_is_creator:

        mock_join_request = MagicMock(user_id=join_request_user_id, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.accept_join_request(user, request_id)

        assert result is False
        assert message == 'Only admins or creator can accept join requests.'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_is_creator.assert_called_once_with(user_id, community_id)

    with patch.object(
            community_service.join_request_repository,
            'get_request_by_id'
        ) as mock_get_request, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=True
         ) as mock_is_admin, \
        patch.object(
            community_service.user_community_repository,
            'add_user_to_community'
        ) as mock_add_user, \
        patch.object(
            community_service.join_request_repository,
            'delete'
         ) as mock_delete_request:

        mock_join_request = MagicMock(user_id=join_request_user_id, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.accept_join_request(user, request_id)

        assert result is True
        assert message == 'Join request accepted successfully.'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_add_user.assert_called_once_with(join_request_user_id, community_id)
        mock_delete_request.assert_called_once_with(request_id)

    with patch.object(
            community_service.join_request_repository,
            'get_request_by_id'
        ) as mock_get_request, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=True
        ) as mock_is_admin, \
        patch.object(
            community_service.user_community_repository,
            'add_user_to_community',
            side_effect=Exception("Accept error")
        ) as mock_add_user, \
        patch.object(
            community_service.join_request_repository,
            'delete'
         ) as mock_delete_request:

        mock_join_request = MagicMock(user_id=join_request_user_id, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.accept_join_request(user, request_id)

        assert result is False
        assert message == 'An error occurred while accepting request to join community. Please try again: Accept error'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_add_user.assert_called_once_with(join_request_user_id, community_id)
        mock_delete_request.assert_not_called()


def test_reject_join_request(community_service):
    user_id = 1
    request_id = 200
    community_id = 100
    user = MagicMock(id=user_id)

    with patch.object(
        community_service.join_request_repository, 'get_request_by_id', return_value=None
    ) as mock_get_request:
        result, message = community_service.reject_join_request(user, request_id)
        assert result is False
        assert message == 'Join request does not exist.'
        mock_get_request.assert_called_once_with(request_id)

    with patch.object(community_service.join_request_repository, 'get_request_by_id') as mock_get_request, \
         patch.object(community_service, 'is_user_community_admin', return_value=False) as mock_is_admin, \
         patch.object(community_service, 'is_user_community_creator', return_value=False) as mock_is_creator:

        mock_join_request = MagicMock(user_id=2, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.reject_join_request(user, request_id)

        assert result is False
        assert message == 'Only admins or creator can reject join requests.'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_is_creator.assert_called_once_with(user_id, community_id)

    with patch.object(community_service.join_request_repository, 'get_request_by_id') as mock_get_request, \
         patch.object(community_service, 'is_user_community_admin', return_value=True) as mock_is_admin, \
         patch.object(community_service.join_request_repository, 'delete') as mock_delete_request:

        mock_join_request = MagicMock(user_id=2, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.reject_join_request(user, request_id)

        assert result is True
        assert message == 'Join request rejected successfully.'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_delete_request.assert_called_once_with(request_id)

    with patch.object(community_service.join_request_repository, 'get_request_by_id') as mock_get_request, \
         patch.object(community_service, 'is_user_community_admin', return_value=True) as mock_is_admin, \
         patch.object(
            community_service.join_request_repository,
            'delete',
            side_effect=Exception("Reject error")
         ) as mock_delete_request:

        mock_join_request = MagicMock(user_id=2, community_id=community_id)
        mock_get_request.return_value = mock_join_request

        result, message = community_service.reject_join_request(user, request_id)

        assert result is False
        assert message == 'An error occurred while rejecting request to join community. Please try again: Reject error'
        mock_get_request.assert_called_once_with(request_id)
        mock_is_admin.assert_called_once_with(user_id, community_id)
        mock_delete_request.assert_called_once_with(request_id)


def test_remove_member(community_service):
    admin_user_id = 1
    member_user_id = 2
    community_id = 100
    admin_user = MagicMock(id=admin_user_id)

    with patch.object(
        community_service.repository, 'get_community_by_id', return_value=None
    ) as mock_get_community:
        result, message = community_service.remove_member(admin_user, community_id, member_user_id)
        assert result is False
        assert message == 'Community does not exist.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=False
         ) as mock_is_member:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.remove_member(admin_user, community_id, member_user_id)

        assert result is False
        assert message == 'User is not a member of this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(member_user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=True
         ) as mock_is_member, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=False
         ) as mock_is_admin, \
        patch.object(
            community_service,
            'is_user_community_creator',
            return_value=False
         ) as mock_is_creator:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.remove_member(admin_user, community_id, member_user_id)

        assert result is False
        assert message == 'Only admins or creator can remove members.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(member_user_id, community_id)
        mock_is_admin.assert_called_once_with(admin_user_id, community_id)
        mock_is_creator.assert_called_once_with(admin_user_id, community_id)


def test_promote_member(community_service):
    admin_user_id = 1
    member_user_id = 2
    community_id = 100
    admin_user = MagicMock(id=admin_user_id)

    with patch.object(community_service.repository, 'get_community_by_id', return_value=None) as mock_get_community:
        result, message = community_service.promote_member(admin_user, community_id, member_user_id)
        assert result is False
        assert message == 'Community does not exist.'
        mock_get_community.assert_called_once_with(community_id)

    with patch.object(community_service.repository, 'get_community_by_id') as mock_get_community, \
         patch.object(
             community_service.user_community_repository,
             'is_user_member_of_community',
             return_value=False
         ) as mock_is_member:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.promote_member(admin_user, community_id, member_user_id)

        assert result is False
        assert message == 'User is not a member of this community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(member_user_id, community_id)

    with patch.object(
            community_service.repository, 'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=True
        ) as mock_is_member, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=False
        ) as mock_is_admin, \
        patch.object(
            community_service,
            'is_user_community_creator',
            return_value=False
         ) as mock_is_creator:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.promote_member(admin_user, community_id, member_user_id)

        assert result is False
        assert message == 'Only admins or creator can remove members.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(member_user_id, community_id)
        mock_is_admin.assert_called_once_with(admin_user_id, community_id)
        mock_is_creator.assert_called_once_with(admin_user_id, community_id)

    with patch.object(
            community_service.repository,
            'get_community_by_id'
        ) as mock_get_community, \
        patch.object(
            community_service.user_community_repository,
            'is_user_member_of_community',
            return_value=True
        ) as mock_is_member, \
        patch.object(
            community_service,
            'is_user_community_admin',
            return_value=True
        ) as mock_is_admin, \
        patch.object(
            community_service,
            'is_user_community_creator',
            side_effect=lambda uid, cid: uid == member_user_id
         ) as mock_is_creator:

        mock_get_community.return_value = MagicMock(id=community_id)
        result, message = community_service.promote_member(admin_user, community_id, member_user_id)

        assert result is False
        assert message == 'You cannot promote the creator of the community.'
        mock_get_community.assert_called_once_with(community_id)
        mock_is_member.assert_called_once_with(member_user_id, community_id)
        mock_is_admin.assert_called_once_with(admin_user_id, community_id)


def test_user_request_pending(community_service):
    user_id = 1
    community_id = 100

    with patch.object(
        community_service.join_request_repository,
        'is_request_already_made',
        return_value=True
    ) as mock_is_request_made:
        result = community_service.user_request_pending(user_id, community_id)
        assert result is True
        mock_is_request_made.assert_called_once_with(user_id, community_id)

    with patch.object(
        community_service.join_request_repository,
        'is_request_already_made',
        return_value=False
    ) as mock_is_request_made:
        result = community_service.user_request_pending(user_id, community_id)
        assert result is False
        mock_is_request_made.assert_called_once_with(user_id, community_id)
