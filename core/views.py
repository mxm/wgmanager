from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from core.models import Community, Shopping
from extra.models import ChatEntry, ShoppingListEntry

def homepage(request):
    return render(request, "index.html")

@login_required()
def dashboard(request):
    vars = {
        'last_shoppings': Shopping.objects.filter(user=request.user)[:5],
        'communities': Community.objects.filter(members=request.user),
    }
    return render(request, "dashboard.html", vars)

@login_required()
def community(request, community):
    vars = {
        'community': get_community(community, request.user),
        'last_shoppings': Shopping.objects.filter(community=community)[:5],
        'my_last_shoppings': Shopping.objects.filter(user=request.user, community=community)[:5],
        'last_list_entries': ShoppingListEntry.objects.filter(community=community, time_done=None),
        'last_messages': ChatEntry.objects.filter(community=community)[:5],
    }
    return render(request, "community.html", vars)

def get_community(community, user):
    try:
        comm_object = Community.objects.get(pk=community)
    except Community.DoesNotExist:
        raise Http404
    if not user in comm_object.members.all():
        raise PermissionDenied
    else:
        return comm_object
