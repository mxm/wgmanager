from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from core.models import Community, Shopping, Bill
from core.models import ChatEntry, ShoppingListEntry
from myauth.models import MyUser

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView


def homepage(request):
    return render(request, "index.html")

@login_required()
def dashboard(request):
    vars = {
        'last_shoppings': Shopping.objects.filter(user=request.user)[:5],
        'communities': Community.objects.filter(members=request.user),
    }
    return render(request, "dashboard.html", vars)

class CommunityView(DetailView):
    model = Community
    template_name = "community.html"

    def get_object(self):
        obj = super(CommunityView, self).get_object()
        if not self.request.user.check_perms(obj):
            raise PermissionDenied
        return obj

class CommunityCreate(CreateView):
    model = Community
    # TODO give own template
    template_name = "generic_form.html"
    #template_name = "community_form.html"
    fields = ['name', 'members']

    def get_form(self, form_class):
        form = super(CommunityCreate, self).get_form(form_class)
        form.fields['members'].queryset = User.objects.exclude(id=self.request.user.id)
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
    fields = ['shopping_day', 'shop', 'expenses', 'billing', 'num_products', 'tags', 'comment']

class ShoppingCreate(ShoppingView, CreateView):

    def form_valid(self, form):
        form.instance.community = get_community(self.kwargs['community_id'], self.request.user)
        form.instance.user = self.request.user
        return super(ShoppingCreate, self).form_valid(form)

class ShoppingUpdate(ShoppingView, UpdateView):
    def get_object(self):
        community = get_community(self.kwargs['community_id'])
        obj = super(ShoppingUpdate, self).get_object()
        if not self.request.user.check_perms(community, obj):
            raise PermissionDenied
        return obj

# TODO
class ShoppingDelete(DeleteView):
    model = Shopping
    template_name = "shopping_confirm_delete.html"


class ViewBill(DetailView):
    model = Bill
    template_name = "bill.html"

    def get_object(self):
        community = get_community(self.kwargs['community_id'])
        obj = super(ViewBill, self).get_object()
        if not self.request.user.check_perms(community):
            raise PermissionDenied
        return obj

def get_community(community_id):
    try:
        comm_object = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        raise Http404
    return comm_object

def get_community_object(community_id, obj_class, obj_id, user=None):
    try:
        obj = obj_class.objects.get(id=obj_id, community=community_id)
    except obj_class.DoesNotExist:
        raise Http404
    if user and obj.user != user:
        raise PermissionDenied
    return obj
