from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("delete/<uuid:asset_id>/", views.delete_ticket, name="delete_ticket"),
    path("update/<uuid:asset_id>/", views.edit_ticket, name="edit_ticket"),
]
