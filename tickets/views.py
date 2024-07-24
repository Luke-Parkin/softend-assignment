from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Ticket


def ticket_list(request):
    # If posting to this endpoint, a ticket is being sent.
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        Ticket.objects.create(title=title, description=description)
        return redirect("ticket_list")

    tickets = Ticket.objects.all().order_by("-created_at")
    return render(request, "board.html", {"tickets": tickets})


def delete_ticket(request, ticket_id):
    Ticket.objects.get(id=ticket_id).delete()
    return JsonResponse({"status": "success"})
