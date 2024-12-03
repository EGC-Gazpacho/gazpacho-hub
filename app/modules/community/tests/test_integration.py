import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

        user_test = User(email='otheruser@example.com', password='password1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_get_community_index(test_client):
    """
    Test retrieving the community index page via GET request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    response = test_client.post('/community/create', data={
        'name': 'Test Community',
        'description': 'This is a test community.',
        'type': 'public'  # Pass the type as a string matching the Enum value
    }, follow_redirects=True)
    assert response.status_code == 200, "Failed to create the community."

    # Verify the community exists in the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Test Community').first()
        assert community is not None, "Community was not found in the database."

    # Access the community index page
    response = test_client.get('/community')
    assert response.status_code == 200, "The community index page could not be accessed."
    assert b"Test Community" in response.data, "The community name is not present on the page."
    assert b"This is a test community." in response.data, "The community description is not present on the page."

    logout(test_client)


def test_get_community_detail(test_client):
    """
    Test retrieving the details of a specific community via GET request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Detail Test Community',
        'description': 'A community to test details.',
        'type': 'public'
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community, UserCommunity, UserRole
        community = Community.query.filter_by(name='Detail Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

        # Verify the user is added as a member with the CREATOR role
        user_community = UserCommunity.query.filter_by(community_id=community_id).first()
        assert user_community is not None, "The creator is not a member of the community."
        assert user_community.role == UserRole.CREATOR, "The creator's role is not set as CREATOR."

    # Access the community detail page
    response = test_client.get(f'/community/{community_id}')
    assert response.status_code == 200, "The community detail page could not be accessed."
    html_content = response.data.decode()

    # Verify the community details
    assert "Detail Test Community" in html_content, "The community name is not present on the page."
    assert "A community to test details." in html_content, "The community description is not present on the page."

    # Verify actions for the creator
    assert "Administrate Community" in html_content, "The 'Administrate Community' button is not present."
    assert "Edit Community" in html_content, "The 'Edit Community' button is not present."
    assert "Delete Community" in html_content, "The 'Delete Community' button is not present."
    assert "Members" in html_content, "The 'Members' section is not present."

    logout(test_client)


def test_edit_community(test_client):
    """
    Test editing a community via GET and POST requests.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Edit Test Community',
        'description': 'A community to test editing.',
        'type': 'public'
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Edit Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Access the edit page via GET
    response = test_client.get(f'/community/edit/{community_id}')
    assert response.status_code == 200, "The community edit page could not be accessed."
    html_content = response.data.decode()
    assert "Edit Test Community" in html_content, "The community name is not pre-filled in the edit form."
    assert "A community to test editing." in html_content, "The community description is not filled in the form."

    # Submit changes via POST
    response = test_client.post(f'/community/edit/{community_id}', data={
        'name': 'Updated Community',
        'description': 'This is the updated description.'
    }, follow_redirects=True)
    assert response.status_code == 200, "Failed to update the community."
    html_content = response.data.decode()
    assert "Updated Community" in html_content, "The updated community name is not displayed."
    assert "This is the updated description." in html_content, "The updated community description is not displayed."

    # Verify the changes in the database
    with test_client.application.app_context():
        updated_community = Community.query.get(community_id)
        assert updated_community is not None, "The updated community could not be found in the database."
        assert updated_community.name == "Updated Community", "The community name was not updated in the database."
        assert updated_community.description == "This is the updated description.", \
            "The community description was not updated in the database."

    logout(test_client)


def test_edit_community_unauthorized(test_client):
    """
    Test that a non-creator cannot edit a community.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Unauthorized Test Community',
        'description': 'A community for unauthorized testing.',
        'type': 'public'
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Log out and log in as a different user
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Attempt to access the edit page
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Unauthorized Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    response = test_client.get(f'/community/edit/{community_id}', follow_redirects=True)
    assert response.status_code == 200, "Unauthorized user could not access the redirect page."

    logout(test_client)


def test_delete_community(test_client):
    """
    Test deleting a community via POST request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Delete Test Community',
        'description': 'A community to test deletion.',
        'type': 'public'
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Delete Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Delete the community via POST request
    delete_response = test_client.post(f'/community/delete/{community_id}', follow_redirects=True)
    assert delete_response.status_code == 200, "Failed to delete the community."

    # Verify the community no longer exists in the database
    with test_client.application.app_context():
        deleted_community = Community.query.get(community_id)
        assert deleted_community is None, "The community was not deleted from the database."

    logout(test_client)


def test_delete_community_unauthorized(test_client):
    """
    Test that a non-creator cannot delete a community.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Unauthorized Delete Test Community',
        'description': 'A community to test unauthorized deletion.',
        'type': 'public'
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Unauthorized Delete Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out and log in as a different user
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Attempt to delete the community
    delete_response = test_client.post(f'/community/delete/{community_id}', follow_redirects=True)
    assert delete_response.status_code == 200, "Unauthorized user could not access the redirect page."

    # Verify the community still exists in the database
    with test_client.application.app_context():
        community = Community.query.get(community_id)
        assert community is not None, "The community was deleted by an unauthorized user."

    logout(test_client)


def test_join_public_community(test_client):
    """
    Test joining a public community via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a public community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Public Test Community',
        'description': 'A public community for testing.',
        'type': 'public'  # Public community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the public community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Public Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in a different user
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Join the public community via the endpoint
    join_response = test_client.post(f'/community/join/{community_id}', follow_redirects=True)
    assert join_response.status_code == 200, "Failed to join the public community."

    # Verify the different user was added to the community
    with test_client.application.app_context():
        from app.modules.community.models import UserCommunity, UserRole
        from app.modules.auth.models import User
        user_community = (
            UserCommunity.query
            .join(User)
            .filter(UserCommunity.community_id == community_id, User.email == "otheruser@example.com")
            .first()
        )
        assert user_community is not None, "The user was not added to the community."
        assert user_community.role == UserRole.MEMBER, "The user was not added with the MEMBER role."

    logout(test_client)


def test_leave_community(test_client):
    """
    Test leaving a community via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a public community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Leave Test Community',
        'description': 'A community to test leaving functionality.',
        'type': 'public'  # Public community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Leave Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in a different user to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Join the public community
    join_response = test_client.post(f'/community/join/{community_id}', follow_redirects=True)
    assert join_response.status_code == 200, "Failed to join the community."

    # Leave the community via the endpoint
    leave_response = test_client.post(f'/community/leave/{community_id}', follow_redirects=True)
    assert leave_response.status_code == 200, "Failed to leave the community."

    # Verify the user is no longer a member of the community
    with test_client.application.app_context():
        from app.modules.community.models import UserCommunity
        from app.modules.auth.models import User
        user_community = (
            UserCommunity.query
            .join(User)
            .filter(UserCommunity.community_id == community_id, User.email == "otheruser@example.com")
            .first()
        )
        assert user_community is None, "The user is still a member of the community after leaving."

    logout(test_client)


def test_request_join_private_community(test_client):
    """
    Test requesting to join a private community via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Request Join Test Community',
        'description': 'A private community for testing join requests.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Request Join Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in a different user to request to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Request to join the private community
    request_response = test_client.post(f'/community/request-join/{community_id}', follow_redirects=True)
    assert request_response.status_code == 200, "Failed to request to join the private community."

    # Verify the join request exists in the database
    with test_client.application.app_context():
        from app.modules.community.models import JoinRequest
        join_request = JoinRequest.query.filter_by(community_id=community_id).first()
        assert join_request is not None, "The join request was not created in the database."
        assert join_request.user.email == "otheruser@example.com", "The join request is not associated with the user."

    logout(test_client)


def test_admin_community_access(test_client):
    """
    Test accessing the community admin page as the creator or admin.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Admin Test Community',
        'description': 'A community to test admin access.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Admin Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Access the admin page as the creator
    admin_response = test_client.get(f'/community/{community_id}/admin')
    assert admin_response.status_code == 200, "The creator could not access the admin page."
    html_content = admin_response.data.decode()
    assert "Admin Test Community" in html_content, "The community name is not displayed on the admin page."

    # Log out the creator and log in as a different user
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Attempt to access the admin page as a non-admin
    unauthorized_response = test_client.get(f'/community/{community_id}/admin', follow_redirects=True)
    assert unauthorized_response.status_code == 200, "Non-admin user could not access the redirected page."

    logout(test_client)


def test_accept_join_request(test_client):
    """
    Test accepting a join request via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Accept Request Test Community',
        'description': 'A private community for testing join request acceptance.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Accept Request Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in as a different user to request to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Request to join the private community
    request_response = test_client.post(f'/community/request-join/{community_id}', follow_redirects=True)
    assert request_response.status_code == 200, "Failed to request to join the private community."

    # Get the join request ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import JoinRequest
        join_request = JoinRequest.query.filter_by(community_id=community_id).first()
        assert join_request is not None, "Join request was not found in the database."
        request_id = join_request.id

    # Log out the requester and log back in as the community creator to accept the request
    logout(test_client)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Failed to log back in as the community creator."

    # Accept the join request
    accept_response = test_client.post(f'/community/{community_id}/requests/{request_id}/accept', follow_redirects=True)
    assert accept_response.status_code == 200, "Failed to accept the join request."

    # Verify the user was added as a member
    with test_client.application.app_context():
        from app.modules.community.models import UserCommunity, UserRole
        user_community = UserCommunity.query.filter_by(community_id=community_id, user_id=join_request.user_id).first()
        assert user_community is not None, "The user was not added to the community."
        assert user_community.role == UserRole.MEMBER, "The user was not added with the MEMBER role."

    logout(test_client)


def test_reject_join_request(test_client):
    """
    Test rejecting a join request via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Reject Request Test Community',
        'description': 'A private community for testing join request rejection.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Reject Request Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in as a different user to request to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Request to join the private community
    request_response = test_client.post(f'/community/request-join/{community_id}', follow_redirects=True)
    assert request_response.status_code == 200, "Failed to request to join the private community."

    # Get the join request ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import JoinRequest
        join_request = JoinRequest.query.filter_by(community_id=community_id).first()
        assert join_request is not None, "Join request was not found in the database."
        request_id = join_request.id

    # Log out the requester and log back in as the community creator to reject the request
    logout(test_client)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Failed to log back in as the community creator."

    # Reject the join request
    reject_response = test_client.post(f'/community/{community_id}/requests/{request_id}/reject', follow_redirects=True)
    assert reject_response.status_code == 200, "Failed to reject the join request."

    # Verify the join request no longer exists in the database
    with test_client.application.app_context():
        join_request = JoinRequest.query.filter_by(community_id=community_id, id=request_id).first()
        assert join_request is None, "The join request was not deleted from the database."

    logout(test_client)


def test_remove_member(test_client):
    """
    Test removing a member from a community via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Remove Member Test Community',
        'description': 'A community to test removing members.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Remove Member Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in as a different user to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Join the community
    join_response = test_client.post(f'/community/join/{community_id}', follow_redirects=True)
    assert join_response.status_code == 200, "Failed to join the community."

    # Get the other user's ID from the database
    with test_client.application.app_context():
        from app.modules.auth.models import User
        other_user = User.query.filter_by(email="otheruser@example.com").first()
        assert other_user is not None, "Other user was not found in the database."
        other_user_id = other_user.id

    # Log out the member and log back in as the community creator to remove the member
    logout(test_client)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Failed to log back in as the community creator."

    # Remove the member
    remove_response = test_client.post(f'/community/{community_id}/remove/{other_user_id}', follow_redirects=True)
    assert remove_response.status_code == 200, "Failed to remove the member from the community."

    # Verify the member is no longer part of the community
    with test_client.application.app_context():
        from app.modules.community.models import UserCommunity
        user_community = UserCommunity.query.filter_by(community_id=community_id, user_id=other_user_id).first()
        assert user_community is None, "The user was not removed from the community."

    logout(test_client)


def test_promote_member_to_admin(test_client):
    """
    Test promoting a community member to admin via POST request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a private community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'Promote Member Test Community',
        'description': 'A community to test member promotion.',
        'type': 'private'  # Private community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the private community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='Promote Member Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in as a different user to request to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Request to join the private community
    request_response = test_client.post(f'/community/request-join/{community_id}', follow_redirects=True)
    assert request_response.status_code == 200, "Failed to request to join the community."

    # Get the join request ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import JoinRequest
        join_request = JoinRequest.query.filter_by(community_id=community_id).first()
        assert join_request is not None, "Join request was not found in the database."
        request_id = join_request.id

    # Log out the requester and log back in as the community creator to accept the request
    logout(test_client)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Failed to log back in as the community creator."

    # Accept the join request
    accept_response = test_client.post(f'/community/{community_id}/requests/{request_id}/accept', follow_redirects=True)
    assert accept_response.status_code == 200, "Failed to accept the join request."

    # Get the other user's ID from the database
    with test_client.application.app_context():
        from app.modules.auth.models import User
        other_user = User.query.filter_by(email="otheruser@example.com").first()
        assert other_user is not None, "Other user was not found in the database."
        other_user_id = other_user.id

    # Promote the member to admin
    promote_response = test_client.post(f'/community/{community_id}/promote/{other_user_id}', follow_redirects=True)
    assert promote_response.status_code == 200, "Failed to promote the member to admin."

    # Verify the member's role is now admin
    with test_client.application.app_context():
        from app.modules.community.models import UserCommunity, UserRole
        user_community = UserCommunity.query.filter_by(community_id=community_id, user_id=other_user_id).first()
        assert user_community is not None, "The user is not part of the community."
        assert user_community.role == UserRole.ADMIN, "The user's role was not updated to ADMIN."

    logout(test_client)


def test_user_communities(test_client):
    """
    Test retrieving the communities a user is a member of via GET request.
    """
    # Log in the test user (creator of the community)
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a public community via the endpoint
    create_response = test_client.post('/community/create', data={
        'name': 'User Communities Test Community',
        'description': 'A community to test user communities retrieval.',
        'type': 'public'  # Public community
    }, follow_redirects=True)
    assert create_response.status_code == 200, "Failed to create the public community."

    # Get the community ID from the database
    with test_client.application.app_context():
        from app.modules.community.models import Community
        community = Community.query.filter_by(name='User Communities Test Community').first()
        assert community is not None, "Community was not found in the database."
        community_id = community.id

    # Log out the creator and log in as a different user to join the community
    logout(test_client)
    login_response = login(test_client, "otheruser@example.com", "password1234")
    assert login_response.status_code == 200, "Failed to log in as a different user."

    # Join the public community
    join_response = test_client.post(f'/community/join/{community_id}', follow_redirects=True)
    assert join_response.status_code == 200, "Failed to join the community."

    # Access the user-communities page
    user_communities_response = test_client.get('/user-communities', follow_redirects=True)
    assert user_communities_response.status_code == 200, "Failed to access the user communities page."
    html_content = user_communities_response.data.decode()

    # Verify the community is listed in the user's communities
    assert "User Communities Test Community" in html_content, "The community name is not displayed in user communities."
    assert "A community to test user communities retrieval." in html_content, "Description is not displayed"

    logout(test_client)
