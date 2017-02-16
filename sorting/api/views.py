from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, viewsets
from rest_framework.decorators import detail_route, renderer_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.renderers import AdminRenderer, BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from api.serializers import ProjectSerializer, JobSerializer, ScriptSerializer
from kron.models import Project, Job, Script
# Create your views here.


class IsOwnerOrPublic(IsAuthenticated):
  def has_object_permission(self, request, view, obj):
    if request.user == obj.owner: return True
    # TODO: admin can do anything
    if request.method in SAFE_METHODS:
        return obj.public
    return False

class ProjectViewSet(viewsets.ModelViewSet):
  """
  Allows projects to be viewed or edited.
  
  retrieve:
  Return a project instance.
  
  run:
  Runs the project.
  
  scripts:
  Returns a list of scripts related to this project.
  """
  queryset = Project.objects.all()
  serializer_class = ProjectSerializer
  renderer_classes = (JSONRenderer,BrowsableAPIRenderer,AdminRenderer,)
  filter_backends = [SearchFilter]
  search_fields = ['name', 'id']
#  permission_classes = [IsOwnerOrPublic]

  def get_queryset(self):
    if self.request.user.is_staff: return self.queryset
    if self.request.user.is_anonymous: return self.queryset.filter(public=True)
    return self.queryset.filter(Q(owner=self.request.user) | Q(public=True))
  
  @detail_route(methods=['post', 'get'])
  def run(self, request, pk=None):
    """
    Runs the project.
    """
    project = Project.objects.get(pk=pk)
    job = project.run(request.user)
    serializer = JobSerializer(job, context={'request': request})
    return Response(serializer.data)
    
  @detail_route()
  def jobs(self, request, pk=None):
    """
    Returns a list of jobs related to this project.
    """
    project = Project.objects.get(pk=pk)
    serializer = JobSerializer(project.jobs.all(), many=True, context={'request': request})
    return Response(serializer.data)

  @detail_route()
  def share(self, request, pk=None):
    project = Project.objects.get(pk=pk)
    if project.owner != request.user:
      return HttpResponseForbidden()
    project.public = True
    project.save()
    serializer = self.serializer_class(project, context={'request': request})
    return Response(serializer.data)

  @detail_route()
  def unshare(self, request, pk=None):
    project = Project.objects.get(pk=pk)
    if project.owner != request.user:
      return HttpResponseForbidden()
    project.public = False
    project.save()
    serializer = self.serializer_class(project, context={'request': request})
    return Response(serializer.data)

class JobViewSet(viewsets.ModelViewSet):
  queryset = Job.objects.all()
  serializer_class = JobSerializer

  def get_queryset(self):
    if self.request.user.is_staff: return self.queryset
    if self.request.user.is_anonymous: return self.queryset.filter(project__public = True)
    return self.queryset.filter(Q(owner=self.request.user) | Q(public=True))


class ScriptViewSet(viewsets.ModelViewSet):
  queryset = Script.objects.all()
  serializer_class = ScriptSerializer

def script_run(request):
  serializer = ScriptSerializer()
  
  return Response(serializer.data)
