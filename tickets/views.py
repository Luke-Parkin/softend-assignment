from logging import getLogger
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Ticket
from .models import AssetCategories

logger = getLogger(__name__)


@login_required
def dashboard(request):
    # If posting to this endpoint, a ticket is being submitted.
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Server side validation
        if title == None or description == None:
            # Front end does not allow 'None' in title or descr, so if this point is reached it is likely this endpoint
            # is not reached via the front end, so a JSON response is sent.
            logger.info("Title or Description are 'None' for ticket Post, invalid.")
            return JsonResponse({"status": "Invalid post request"})

        if request.user.is_superuser:
            # we do not enforce a username requirement, owners do not have to have user accounts
            user = request.POST.get("username") or request.user.username
        else:
            # since login_required, this will always be true
            user = request.user.username

        ticket = Ticket.objects.create(
            asset_title=title,
            user_owner=user,
            asset_description=description,
            category=AssetCategories.LAPTOP,
        )
        logger.info(f"Asset created, id={ticket.asset_id}")

        return redirect(reverse("dashboard") + f"?newt={ticket.asset_id}")

    # Check for events
    delete_success = request.GET.get("delete", None)
    new_ticket = request.GET.get("newt", None)

    tickets = Ticket.objects.all().order_by("-created_at")
    return render(
        request,
        "board.html",
        {"tickets": tickets, "deleted": delete_success, "new_ticket": new_ticket},
    )


# Do not need to check if asset exists here, this is checked since urls.py requires the asset_id path exists
@login_required
def delete_ticket(request, asset_id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            Ticket.objects.get(asset_id=asset_id).delete()
            logger.info(f"SuperUser {request.user.username} deleted {asset_id}")
            return JsonResponse({"status": "success"})
        elif request.user.username == Ticket.objects.get(asset_id=asset_id).user_owner:
            Ticket.objects.get(asset_id=asset_id).delete()
            logger.warn(f"User {request.user.username} deleted {asset_id}")
            return JsonResponse({"status": "success"})
        else:
            logger.warn(
                f"User {request.user.username} is not authorised to delete ticket {asset_id}"
            )
            return JsonResponse({"status": "unauthorized"})
    logger.info(f"User is not authenticated to delete {asset_id}")
    return JsonResponse({"status": "unauthenticated"})


# Do not need to check if asset exists here, this is checked since urls.py requires the asset_id path exists
@login_required
def edit_ticket(request, asset_id):
    if request.method == "POST":

        asset = Ticket.objects.get(asset_id=request.POST.get("asset_id"))

        if request.user.is_superuser:
            user = request.POST.get("owner") or request.user.username
        else:
            user = request.user.username

        asset.asset_title = request.POST.get("title") or asset.asset_title
        asset.user_owner = user
        asset.asset_description = (
            request.POST.get("description") or asset.asset_description
        )
        # asset.category = AssetCategories.LAPTOP

        asset.save()
        return redirect(reverse("dashboard") + f"?newt={asset.asset_id}")

    asset = Ticket.objects.get(asset_id=asset_id)

    if asset.user_owner == request.user.username or request.user.is_superuser:
        return render(request, "edit.html", {"asset": asset})
    else:
        return JsonResponse({"status": "no_permissions"})


def asset_not_found(request):
    return render(request, "asset-404.html")
