from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Ticket
from .models import AssetCategories


@login_required
def dashboard(request):
    # If posting to this endpoint, a ticket is being submitted.
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Server side validation
        if request.user.is_superuser:
            user = request.POST.get("username") or request.user.username
        else:
            user = request.user.username

        ticket = Ticket.objects.create(
            asset_title=title,
            user_owner=user,
            asset_description=description,
            category=AssetCategories.LAPTOP,
        )
        return redirect(reverse("dashboard") + f"?newt={ticket.asset_id}")

    delete_success = request.GET.get("delete", None)
    new_ticket = request.GET.get("newt", None)

    tickets = Ticket.objects.all().order_by("-created_at")
    return render(
        request,
        "board.html",
        {"tickets": tickets, "deleted": delete_success, "new_ticket": new_ticket},
    )


def delete_ticket(request, ticket_id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            Ticket.objects.get(asset_id=ticket_id).delete()
            return JsonResponse({"status": "success"})
        elif request.user.username == Ticket.objects.get(asset_id=ticket_id).user_owner:
            Ticket.objects.get(asset_id=ticket_id).delete()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "unauthorized"})
