from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("delete/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
]
