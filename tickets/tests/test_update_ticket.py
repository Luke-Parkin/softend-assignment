import pytest
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock
from tickets.models import Ticket

from tickets.views import edit_ticket


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
    user.username = "regular_user"
    return user


@pytest.fixture
def mock_ticket():
    ticket = MagicMock()
    ticket.asset_id = "123"
    ticket.asset_title = "Original Title"
    ticket.user_owner = "regular_user"
    ticket.asset_description = "Original Description"
    return ticket


# Given a superuser
# Returns the edit-ticket view
@patch("tickets.views.render")
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_get_superuser(
    mock_get, mock_render, factory, mock_superuser, mock_ticket
):
    mock_get.return_value = mock_ticket
    mock_render.return_value = HttpResponse()  # Simulate render response
    request = factory.get(f"/edit-ticket/{mock_ticket.asset_id}/")
    request.user = mock_superuser

    edit_ticket(request, asset_id=mock_ticket.asset_id)

    mock_get.assert_called_once_with(asset_id=mock_ticket.asset_id)
    mock_render.assert_called_once_with(request, "edit.html", {"asset": mock_ticket})


# Given a user,
# who owns the asset
# returns the edit_ticket view
@patch("tickets.views.render")
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_get_owner(
    mock_get, mock_render, factory, mock_regular_user, mock_ticket
):
    mock_get.return_value = mock_ticket
    mock_render.return_value = HttpResponse()  # Simulate render response
    request = factory.get(f"/edit-ticket/{mock_ticket.asset_id}/")
    request.user = mock_regular_user

    edit_ticket(request, asset_id=mock_ticket.asset_id)

    mock_get.assert_called_once_with(asset_id=mock_ticket.asset_id)
    mock_render.assert_called_once_with(request, "edit.html", {"asset": mock_ticket})


# Given a POST edit by a user,
# who does not have permissions
# returns no_permissions obj
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_get_unauthorized(
    mock_get, factory, mock_regular_user, mock_ticket
):
    mock_ticket.user_owner = "other_user"
    mock_get.return_value = mock_ticket
    request = factory.get(f"/edit-ticket/{mock_ticket.asset_id}/")
    request.user = mock_regular_user

    response = edit_ticket(request, asset_id=mock_ticket.asset_id)

    mock_get.assert_called_once_with(asset_id=mock_ticket.asset_id)
    assert isinstance(response, JsonResponse)
    assert response.content.decode("utf-8") == '{"status": "no_permissions"}'


# Given a POST edit from a superuser
# With a new owner
# changes the owner and edits the ticket
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_post_superuser(mock_get, factory, mock_superuser, mock_ticket):
    mock_get.return_value = mock_ticket
    request = factory.post(
        f"/edit-ticket/{mock_ticket.asset_id}/",
        {
            "asset_id": mock_ticket.asset_id,
            "title": "Titlev2",
            "description": "Description: but better",
            "owner": "new_owner",
        },
    )
    request.user = mock_superuser

    response = edit_ticket(request, asset_id=mock_ticket.asset_id)

    mock_get.assert_called_once_with(asset_id=mock_ticket.asset_id)
    assert mock_ticket.asset_title == "Titlev2"
    assert mock_ticket.asset_description == "Description: but better"
    assert mock_ticket.user_owner == "new_owner"
    mock_ticket.save.assert_called_once()
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("dashboard") + f"?newt={mock_ticket.asset_id}"


# Given an edit post
# from a regular user who tries to edit the owner
# edits the ticket, without changing the owner
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_post_regular_user(
    mock_get, factory, mock_regular_user, mock_ticket
):
    mock_get.return_value = mock_ticket
    request = factory.post(
        f"/edit-ticket/{mock_ticket.asset_id}/",
        {
            "asset_id": mock_ticket.asset_id,
            "title": "Title? Yeah, this is a title.",
            "description": "Description2",
            "owner": "new_owner",
        },
    )
    request.user = mock_regular_user

    response = edit_ticket(request, asset_id=mock_ticket.asset_id)

    mock_get.assert_called_once_with(asset_id=mock_ticket.asset_id)
    assert mock_ticket.asset_title == "Title? Yeah, this is a title."
    assert mock_ticket.asset_description == "Description2"
    assert mock_ticket.user_owner == "regular_user"  # user_owner should be unchanged
    mock_ticket.save.assert_called_once()
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("dashboard") + f"?newt={mock_ticket.asset_id}"


# Given an unauthenticated user,
# Redirects them without editing the database
@patch("tickets.views.Ticket.objects.get")
def test_edit_ticket_redirects_unauthenticated_user(mock_get):
    factory = RequestFactory()
    request = factory.get("/edit-ticket/999/")
    request.user = AnonymousUser()
    mock_get.return_value = MagicMock(spec=Ticket)  # Mock the Ticket object

    response = edit_ticket(request, asset_id="999")

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == "/?next=/edit-ticket/999/"
    mock_get.assert_not_called()
