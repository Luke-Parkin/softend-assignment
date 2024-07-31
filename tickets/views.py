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


@login_required
def delete_ticket(request, asset_id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            Ticket.objects.get(asset_id=asset_id).delete()
            return JsonResponse({"status": "success"})
        elif request.user.username == Ticket.objects.get(asset_id=asset_id).user_owner:
            Ticket.objects.get(asset_id=asset_id).delete()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "unauthorized"})


@login_required
def edit_ticket(request, asset_id):
    if request.method == "POST":
        asset = Ticket.objects.get(asset_id=request.POST.get("asset_id"))
        if not asset:
            print("appropriate error again")

        if request.user.is_superuser:
            user = request.POST.get("owner") or request.user.username
        else:
            user = request.user.username
        asset.asset_title = request.POST.get("title") or asset.asset_title
        asset.user_owner = user
        asset.asset_description = (
            request.POST.get("description") or asset.asset_description
        )
        asset.save()
        # asset.category = AssetCategories.LAPTOP
        return redirect(reverse("dashboard") + f"?newt={asset.asset_id}")

    asset = Ticket.objects.get(asset_id=asset_id)
    if asset.user_owner == request.user.username or request.user.is_superuser:
        return render(request, "edit.html", {"asset": asset})
    else:
        print("no permissions - fix this error later.")
        return JsonResponse({"status": "noperms"})
