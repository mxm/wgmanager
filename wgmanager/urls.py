from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wgmanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^$', 'core.views.homepage'),

    url(r'^dashboard/$', 'core.views.dashboard'),

    url(r'^community/(\d)/$', 'core.views.community'),
    url(r'^community/(\d)/add/shopping/$', 'core.views.add_shopping'),



    url(r'^login.html$', 'django.contrib.auth.views.login',
        {'template_name':'login.html'}),
    url(r'^logout.html$', 'django.contrib.auth.views.logout',{'template_name':'logout.html'}),
)
