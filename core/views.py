from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from core.models import Community, Shopping
from extra.models import ChatEntry, ShoppingListEntry

from core.forms import ShoppingForm

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
def community(request, community_id):
    vars = {
        'community': get_community(community_id, request.user),
        'last_shoppings': Shopping.objects.filter(community=community_id)[:5],
        'my_last_shoppings': Shopping.objects.filter(user=request.user, community=community_id)[:5],
        'last_list_entries': ShoppingListEntry.objects.filter(community=community_id, time_done=None),
        'last_messages': ChatEntry.objects.filter(community=community_id)[:5],
    }
    return render(request, "community.html", vars)

@login_required()
def add_shopping(request, community_id):
    community = get_community(community_id, request.user)
    if request.method == "POST":
        form = ShoppingForm(request.POST)
        if form.is_valid():
            shopping = form.save(commit=False)
            shopping.community = community
            shopping.user = request.user
            shopping.save()
            return redirect(community.get_absolute_url())
    else:
        form = ShoppingForm()
    vars = {'form': form
    }
    return render(request, "shopping.html", vars)


def get_community(community_id, user):
    try:
        comm_object = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        raise Http404
    if not user in comm_object.members.all():
        raise PermissionDenied
    else:
        return comm_object
