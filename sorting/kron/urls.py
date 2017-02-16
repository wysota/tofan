from django.conf.urls import url

from kron.views import ProjectList, ProjectDetail, ProjectUpdate, JobDetail, RunJobView
from kron.views import DaemonStateView

urlpatterns = [
    url(r'^$', ProjectList.as_view(), name='projects-list'),
    url(r'^(?P<pk>[0-9]+)/$', ProjectDetail.as_view(), name='projects-detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', ProjectUpdate.as_view(), name='projects-edit'),
    url(r'^(?P<pk>[0-9]+)/run/$', RunJobView.as_view(), name='projects-run'),
    url(r'^jobs/(?P<pk>[0-9]+)/$', JobDetail.as_view(), name='jobs-detail'),
    url(r'^daemon-state/$', DaemonStateView.as_view(), name='daemon-state'),
]
