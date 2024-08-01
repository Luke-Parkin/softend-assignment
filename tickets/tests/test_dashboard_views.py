import pytest
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock

from tickets.views import dashboard
from tickets.models import AssetCategories


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.username = "testuser"
    user.is_superuser = False
    user.is_authenticated = True
    return user


@pytest.fixture
def mock_superuser():
    user = MagicMock()
    user.username = "admin"
    user.is_superuser = True
    return user


# Given an authorised user,
# Loads the dashboard
@patch("tickets.views.render")
@patch("tickets.views.Ticket.objects.all")
def test_dashboard_get(mock_all, mock_render, factory, mock_user):
    request = factory.get(reverse("dashboard"))
    request.user = mock_user
    mock_all.return_value.order_by.return_value = []
    mock_render.return_value = HttpResponse()  # Simulate the render function

    dashboard(request)

    mock_all.assert_called_once()
    mock_all.return_value.order_by.assert_called_once_with("-created_at")
    mock_render.assert_called_once_with(
        request, "board.html", {"tickets": [], "deleted": None, "new_ticket": None}
    )


# Given a post request to the dashboard,
# With a valid user,
# Creates a ticket and redirects back to the dashboard with the asset_id
@patch("tickets.views.Ticket.objects.create")
def test_dashboard_post_valid(mock_create, factory, mock_user):
    request = factory.post(
        reverse("dashboard"), {"title": "Test Title", "description": "Test Description"}
    )
    request.user = mock_user
    mock_ticket = MagicMock()
    mock_ticket.asset_id = "12345"
    mock_create.return_value = mock_ticket

    response = dashboard(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
    assert response.url == reverse("dashboard") + "?newt=12345"
    mock_create.assert_called_once_with(
        asset_title="Test Title",
        user_owner="testuser",
        asset_description="Test Description",
        category=AssetCategories.LAPTOP,
    )


# Given an invalid post request,
# With no valid fields,
# Returns a json response reporting invalid request.
@patch("tickets.views.Ticket.objects.create")
def test_dashboard_post_invalid(mock_create, factory, mock_user):
    request = factory.post(reverse("dashboard"), {})
    request.user = mock_user

    response = dashboard(request)

    assert isinstance(response, JsonResponse)
    assert response.content.decode("utf-8") == '{"status": "Invalid post request"}'
    mock_create.assert_not_called()


# Given a post request,
# from a superuser,
# Allows a custom username to be given and set
@patch("tickets.views.Ticket.objects.create")
def test_dashboard_post_superuser(mock_create, factory, mock_superuser):
    request = factory.post(
        reverse("dashboard"),
        {
            "title": "Test Title",
            "description": "Test Description",
            "username": "customuser",
        },
    )
    request.user = mock_superuser
    mock_ticket = MagicMock()
    mock_ticket.asset_id = "12345"
    mock_create.return_value = mock_ticket

    response = dashboard(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
    assert response.url == reverse("dashboard") + "?newt=12345"
    mock_create.assert_called_once_with(
        asset_title="Test Title",
        user_owner="customuser",
        asset_description="Test Description",
        category=AssetCategories.LAPTOP,
    )


# Given a post request,
# from a regular user attempting to create asset with custom username,
# It ignores the custom username and uses the users username
@patch("tickets.views.Ticket.objects.create")
def test_dashboard_post_user_without_auth(mock_create, factory, mock_user):
    request = factory.post(
        reverse("dashboard"),
        {
            "title": "Test Title",
            "description": "Test Description",
            "username": "customuser",
        },
    )
    request.user = mock_user
    mock_ticket = MagicMock()
    mock_ticket.asset_id = "12345"
    mock_create.return_value = mock_ticket

    response = dashboard(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
    assert response.url == reverse("dashboard") + "?newt=12345"
    mock_create.assert_called_once_with(
        asset_title="Test Title",
        user_owner=request.user.username,
        asset_description="Test Description",
        category=AssetCategories.LAPTOP,
    )


# Given a call to dashboard,
# With all parameters,
# correctly passes them to the template.
@patch("tickets.views.render")
@patch("tickets.views.Ticket.objects.all")
def test_dashboard_get_with_params(mock_all, mock_render, factory, mock_user):
    request = factory.get(reverse("dashboard") + "?delete=true&newt=12345")
    request.user = mock_user
    mock_all.return_value.order_by.return_value = []
    mock_render.return_value = HttpResponse()

    dashboard(request)

    mock_render.assert_called_once_with(
        request, "board.html", {"tickets": [], "deleted": "true", "new_ticket": "12345"}
    )
