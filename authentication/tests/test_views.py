import os
import django
import pytest
from django.urls import reverse
from unittest import mock
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.test import RequestFactory
from authentication.views import landing, login_page


@pytest.mark.django_db
def test_login_page_invalid_login_redirect():
    factory = RequestFactory()
    request = factory.post(
        reverse("login"), {"username": "invalid", "password": "invalid"}
    )

    response = login_page(request)

    with mock.patch(
        "django.contrib.auth.forms.AuthenticationForm.is_valid", return_value=False
    ):
        # Assert the response is a redirect to the login page with failed=true query
        assert response.status_code == 302
        assert response.url == reverse("login") + "?failed=true"


def test_landing_redirect_authenticated():
    factory = RequestFactory()
    request = factory.get(reverse("landing"))
    request.user = mock.Mock()
    request.user.is_authenticated = True

    response = landing(request)

    assert response.status_code == 302
    assert response.url == reverse("dashboard")


@mock.patch("authentication.views.render")
def test_landing_redirect_unauthenticated(mock_render):
    factory = RequestFactory()
    request = factory.get(reverse("landing"))
    request.user = mock.Mock()
    request.user.is_authenticated = False

    response = landing(request)

    mock_render.assert_called_once_with(request, "landing.html")
