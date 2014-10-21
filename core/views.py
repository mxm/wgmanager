from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from core.models import Community, Shopping
from extra.models import ChatEntry, ShoppingListEntry

from django.views.generic import CreateView, UpdateView, DeleteView


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



class ShoppingView(object):
    model = Shopping
    template_name = "shopping_form.html"
    fields = ['shopping_day', 'shop', 'expenses', 'num_products', 'tags',
              'automatic_billing', 'bill', 'comment']

class ShoppingCreate(ShoppingView, CreateView):
    def form_valid(self, form):
        form.instance.community = get_community(self.kwargs['community_id'], self.request.user)
        form.instance.user = self.request.user
        return super(ShoppingCreate, self).form_valid(form)

class ShoppingUpdate(ShoppingView, UpdateView):
    def get_object(self):
        return get_shopping(self.kwargs['community_id'], self.kwargs['pk'], self.request.user)

# TODO
class ShoppingDelete(DeleteView):
    model = Shopping
    template_name = "shopping_confirm_delete.html"

def get_community(community_id, user):
    try:
        comm_object = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        raise Http404
    if not user in comm_object.members.all():
        raise PermissionDenied
    return comm_object

def get_shopping(community_id, shopping_id, user=None):
    try:
        shopping_object = Shopping.objects.get(pk=shopping_id, community=community_id)
    except Shopping.DoesNotExist:
        raise Http404
    if user and shopping_object.user.id != user.id:
        raise PermissionDenied
    return shopping_object
