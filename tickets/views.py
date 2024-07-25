from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Ticket


@login_required
def dashboard(request):
    # If posting to this endpoint, a ticket is being sent.
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        Ticket.objects.create(title=title, description=description)
        return redirect("dashboard")

    tickets = Ticket.objects.all().order_by("-created_at")
    return render(request, "board.html", {"tickets": tickets})


def delete_ticket(request, ticket_id):
    if request.user.is_authenticated:
        # if request.user.has_perm("some-permission") < in future check has delete permissions
        # if request.user.id == ticket.userid or if user is superuser
        Ticket.objects.get(id=ticket_id).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failure"})
