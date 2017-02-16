from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'scripts', views.ScriptViewSet)

schema_view = get_schema_view(title='KRON API')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^schema/$', schema_view),
#    url(r'projects/$', views.ProjectList.as_view(), name='project-list'),
#    url(r'projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), name='project-detail'),
]

#urlpatterns = format_suffix_patterns(urlpatterns)

