from django.urls import path
from . import views

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("delete/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
]
