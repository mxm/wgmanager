from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from core.models import Community, Shopping
from extra.models import ChatEntry, ShoppingListEntry
from myauth.models import MyUser

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


class CommunityCreate(CreateView):
    model = Community
    # TODO give own template
    template_name = "generic_form.html"
    #template_name = "community_form.html"
    fields = ['name', 'members']

    def get_form(self, form_class):
        form = super(CommunityCreate, self).get_form(form_class)
        form.fields['members'].queryset = MyUser.objects.exclude(id=self.request.user.id)
        return form

    def form_valid(self, form):
        # add ourselves so we can access the new community
        community = form.save()
        community.members.add(self.request.user)
        return HttpResponseRedirect(community.get_absolute_url())


class ShoppingView(object):
    model = Shopping
    # TODO give own template
    template_name = "generic_form.html"
    #template_name = "shopping_form.html"
    fields = ['shopping_day', 'shop', 'expenses', 'num_products', 'tags',
              'automatic_billing', 'bill', 'comment']

class ShoppingCreate(ShoppingView, CreateView):
    def form_valid(self, form):
        form.instance.community = get_community(self.kwargs['community_id'], self.request.user)
        form.instance.user = self.request.user
        return super(ShoppingCreate, self).form_valid(form)

class ShoppingUpdate(ShoppingView, UpdateView):
    def get_object(self):
        return get_community_object(self.kwargs['community_id'], Shopping, self.kwargs['pk'], self.request.user)

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

def get_community_object(community_id, obj_class, obj_id, user=None):
    try:
        obj = obj_class.objects.get(id=obj_id, community=community_id)
    except obj_class.DoesNotExist:
        raise Http404
    if user and obj.user != user:
        raise PermissionDenied
    return obj
