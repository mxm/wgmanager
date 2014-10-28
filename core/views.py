from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from core.models import User, Community, Shopping, Bill
from core.models import ChatEntry, ShoppingListEntry

from django.views.generic import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView


class ProtectedView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProtectedView, self).dispatch(request, *args, **kwargs)


def homepage(request):
    return render(request, "index.html")

@login_required()
def dashboard(request):
    vars = {
        'last_shoppings': Shopping.objects.filter(user=request.user)[:5],
        'communities': Community.objects.filter(members=request.user),
    }
    return render(request, "dashboard.html", vars)

class CommunityView(ProtectedView, DetailView):
    model = Community
    template_name = "community.html"

    def get_object(self, qs=None):
        obj = super(CommunityView, self).get_object(qs)
        fail_on_false_community(self.request.user, obj)
        return obj

class CommunityCreate(ProtectedView, CreateView):
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


class ShoppingView(ProtectedView):
    model = Shopping
    # TODO give own template
    template_name = "generic_form.html"
    #template_name = "shopping_form.html"
    fields = ['shopping_day', 'shop', 'expenses', 'billing', 'num_products', 'tags', 'comment']

class ShoppingCreate(ShoppingView, CreateView):
    def form_valid(self, form):
        community_id = self.kwargs['community_id']
        form.instance.community = get_community_or_fail(community_id, self.request.user)
        form.instance.user = self.request.user
        return super(ShoppingCreate, self).form_valid(form)

class ShoppingUpdate(ShoppingView, UpdateView):
    def get_object(self):
        obj = super(ShoppingUpdate, self).get_object()
        fail_on_false_ownership(self.request.user, obj)
        return obj

class ShoppingDelete(ProtectedView, DeleteView):
    model = Shopping
    template_name = "generic_delete.html"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        fail_on_false_ownership(request.user, obj)
        return super(ShoppingDelete, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('community', args=[self.kwargs['community_id']])


class BillView(ProtectedView, DetailView):
    model = Bill
    template_name = "bill.html"

    def get_object(self):
        obj = super(BillView, self).get_object()
        fail_on_false_community(self.request.user, obj)
        return obj


def fail_on_false_community(user, obj):
    if obj.__class__ == Community:
        if not obj.members.filter(id=user.id).exists():
            raise PermissionDenied
    else:
        if not obj.community.members.filter(id=user.id).exists():
            raise PermissionDenied

def fail_on_false_ownership(user, obj):
    if obj.user != user:
        raise PermissionDenied

def get_community_or_fail(community_id, user):
    try:
        community = Community.objects.get(id=community_id)
    except Community.DoesNotExist:
        raise Http404
    fail_on_false_community(user, community)
    return community
