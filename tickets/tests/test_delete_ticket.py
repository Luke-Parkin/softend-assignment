import pytest
from django.http import JsonResponse, HttpResponseRedirect
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock

from tickets.views import delete_ticket


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def mock_superuser():
    user = MagicMock()
    user.is_authenticated = True
    user.is_superuser = True
    user.username = "admin"
    return user


@pytest.fixture
def mock_regular_user():
    user = MagicMock()
    user.is_authenticated = True
    user.is_superuser = False
    user.username = "regusr"
    return user


@pytest.fixture
def mock_anonymous_user():
    return AnonymousUser()


# Given a request to delete a object,
# With a superuser,
# Deletes the asset.
@patch("tickets.views.Ticket.objects")
def test_delete_ticket_superuser(mock_ticket_objects, factory, mock_superuser):
    mock_ticket = MagicMock()
    mock_ticket_objects.get.return_value = mock_ticket
    request = factory.post("/delete-ticket/")
    request.user = mock_superuser

    response = delete_ticket(request, asset_id="123")

    mock_ticket_objects.get.assert_called_once_with(asset_id="123")
    mock_ticket.delete.assert_called_once()
    assert response.content.decode("utf-8") == '{"status": "success"}'


# Given a request to delete a asset,
# with a regular user who owns the asset,
# deletes the asset
@patch("tickets.views.Ticket.objects")
def test_delete_ticket_owner(mock_ticket_objects, factory, mock_regular_user):
    mock_ticket = MagicMock()
    mock_ticket.user_owner = "regusr"
    mock_ticket_objects.get.return_value = mock_ticket
    request = factory.post("/delete-ticket/")
    request.user = mock_regular_user

    response = delete_ticket(request, asset_id="123")

    assert mock_ticket_objects.get.call_count == 2
    mock_ticket_objects.get.assert_called_with(asset_id="123")
    mock_ticket.delete.assert_called_once()
    assert isinstance(response, JsonResponse)
    assert response.content.decode("utf-8") == '{"status": "success"}'


# Given a request to delete a asset,
# with a regular user who does NOT own the asset
# returns unauthorized
@patch("tickets.views.Ticket.objects")
def test_delete_ticket_unauthorized(mock_ticket_objects, factory, mock_regular_user):
    mock_ticket = MagicMock()
    mock_ticket.user_owner = "other_user"
    mock_ticket_objects.get.return_value = mock_ticket
    request = factory.post("/delete-ticket/")
    request.user = mock_regular_user

    response = delete_ticket(request, asset_id="123")

    mock_ticket_objects.get.assert_called_once_with(asset_id="123")
    mock_ticket.delete.assert_not_called()
    assert isinstance(response, JsonResponse)
    assert response.content.decode("utf-8") == '{"status": "unauthorized"}'


# Given a request to delete an asset
# with a user who is not authenticated
# it redirects them
def test_delete_ticket_unauthenticated(factory, mock_anonymous_user):
    request = factory.post("/delete-ticket/")
    request.user = mock_anonymous_user
    mock_ticket = MagicMock()

    response = delete_ticket(request, asset_id="123")

    mock_ticket.delete.assert_not_called()
    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
