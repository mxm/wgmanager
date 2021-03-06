from django.conf.urls import patterns, include, url
from django.contrib import admin

from core.views import ShoppingCreate, ShoppingUpdate, ShoppingDelete
from core.views import CommunityView, CommunityCreate
from core.views import BillView, BillCreate, BillUpdate
from core.views import PayerCreate, PayerDelete


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wgmanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^$', 'core.views.homepage'),

    url(r'^dashboard/$', 'core.views.dashboard', name='dashboard'),

    url(r'^community/(?P<pk>\d+)/$', CommunityView.as_view(), name='community'),
    url(r'^community/add/$', CommunityCreate.as_view(), name='community_new'),

    url(r'^community/(?P<community_id>\d+)/shopping/add/$', ShoppingCreate.as_view(), name='shopping_new'),

    url(r'^community/(?P<community_id>\d+)/shopping/(?P<pk>\d+)/$', ShoppingUpdate.as_view(), name='shopping'),
    url(r'^community/(?P<community_id>\d+)/shopping/(?P<pk>\d+)/delete/$', ShoppingDelete.as_view(), name='shopping_delete'),

    #url(r'^community/(?P<community_id>\d+)/bill/(?P<bill_id>\d+)/$', 'core.views.view_bill', name='bill'),
    url(r'^community/(?P<community_id>\d+)/bill/(?P<pk>\d+)/$', BillView.as_view(), name='bill'),
    url(r'^community/(?P<community_id>\d+)/bill/add/$', BillCreate.as_view(), name='bill_new'),
    url(r'^community/(?P<community_id>\d+)/bill/(?P<pk>\d+)/edit/$', BillUpdate.as_view(), name='bill_update'),
    #url(r'^community/(?P<community_id>\d+)/bill/(?P<pk>\d+)/$', BillView.as_view(), name='bill_delete'),

    url(r'^community/(?P<community_id>\d+)/bill/(?P<pk>\d+)/close/$', 'core.views.close_bill', name='close_bill'),

    url(r'^community/(?P<community_id>\d+)/bill/(?P<bill_id>\d+)/add_payer/$', PayerCreate.as_view(), name='add_payer'),
    url(r'^community/(?P<community_id>\d+)/bill/(?P<bill_id>\d+)/delete_payer/(?P<pk>\d+)$', PayerDelete.as_view(), name='delete_payer'),

    url(r'^login.html$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}),
    url(r'^logout.html$', 'django.contrib.auth.views.logout',{'template_name':'logout.html'}),
)
