"""sorting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from sorting import settings
from kron.views import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'extra_context': {'breadcrumb': [ { 'url': "/", "label": "MountainSort"}, {'url': '', "label": "Login"}]}}, name='login'),
    url(r'^logout/$', auth_views.logout, {'extra_context': {'breadcrumb': [ { 'url': "/", "label": "MountainSort"}, {'url': '', "label": "Logout"}]}}, name='logout'),
    url(r'^api/', include('api.urls')),
    url(r'^kron/', include('kron.urls')),
    url(r'^$', static, {"page_name": "index"}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

