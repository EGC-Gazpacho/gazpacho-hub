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
