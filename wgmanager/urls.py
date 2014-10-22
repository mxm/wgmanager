from django.conf.urls import patterns, include, url
from django.contrib import admin

from core.views import ShoppingCreate, ShoppingUpdate, ShoppingDelete
from core.views import CommunityCreate

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wgmanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^$', 'core.views.homepage'),

    url(r'^dashboard/$', 'core.views.dashboard', name='dashboard'),

    url(r'^community/(\d+)/$', 'core.views.community'),
    url(r'^community/add/$', login_required(CommunityCreate.as_view()), name='community_new'),

    url(r'^community/(?P<community_id>\d+)/shopping/add/$', login_required(ShoppingCreate.as_view()), name='shopping_new'),
    url(r'^community/(?P<community_id>\d+)/shopping/(?P<pk>\d+)/$', login_required(ShoppingUpdate.as_view()), name='shopping'),
    url(r'^community/(?P<community_id>\d+)/shopping/(?P<pk>\d+)/delete/$', login_required(ShoppingDelete.as_view()), name='shopping_delete'),


    url(r'^login.html$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}),
    url(r'^logout.html$', 'django.contrib.auth.views.logout',{'template_name':'logout.html'}),
)
