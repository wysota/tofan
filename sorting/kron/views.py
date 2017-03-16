from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from kron.models import Project, Job
from sorting.settings import MOUNTAINSORT_SETTINGS
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from django.forms import models as model_forms

from kron.kron import Kron

import subprocess
import json
import os.path

# Create your views here.

class ProjectList(ListView):
    model = Project

    def get_queryset(self):
      if self.request.user.is_anonymous:
        return self.model.objects.filter(public=True)
      if self.request.user.is_staff:
        return super(ProjectList, self).get_queryset()
      return self.model.objects.filter(Q(owner=self.request.user) | Q(public=True))

    def get_context_data(self, **kwargs):
      context = super(ProjectList, self).get_context_data(**kwargs)
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": reverse("projects-list"), "label": "Projects" },
      )
      return context

class ProjectDetail(DetailView):
    model = Project

    def get(self, *args, **kwargs):
      if "share" in self.request.GET:
        obj = self.get_object()
        if obj.owner != self.request.user: return HttpResponseForbidden()
        oldpublic = obj.public
        obj.public = self.request.GET.get("share")=="true"
        if oldpublic != obj.public:
            messages.success(self.request, "Project has been made public." if obj.public else "Project has been made private.")
        obj.save()
      return super(ProjectDetail, self).get(*args, **kwargs)

    def get_object(self, queryset = None):
      obj = super(ProjectDetail, self).get_object(queryset)
      if self.request.user.is_staff: return obj
      if obj.public: return obj
      if obj.owner == self.request.user: return obj
      raise PermissionDenied()

    def get_context_data(self, **kwargs):
      context = super(ProjectDetail, self).get_context_data(**kwargs)
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": reverse("projects-list"), "label": "Projects" },
        {"url": reverse("projects-detail", args=[self.object.id]), "label": self.object.name },
      )
      context["can_start_jobs"] = (not self.request.user.is_anonymous) or (self.object.owner == self.request.user)
      context["is_owner"] = self.object.owner == self.request.user
      context["is_admin"] = self.request.user.is_staff

      if not os.path.isfile(os.path.join(self.object.absolutePath, "pipelines.txt")):
        messages.error(self.request, "Project is probably misconfigured - 'pipelines.txt' doesn't exist.")
      elif not os.path.isfile(os.path.join(self.object.absolutePath, "datasets.txt")):
        messages.error(self.request, "Project is probably misconfigured - 'datasets.txt' doesn't exist.")
      return context

class ProjectUpdate(SuccessMessageMixin, UpdateView):
    model = Project
    fields = ['name', 'description', 'path']
    fields_admin = ['name', 'owner', 'description', 'path']
    success_message = "Project data saved successfully"

    def get_context_data(self, **kwargs):
      if not self.request.user.is_staff and self.request.user != self.object.owner:
        raise PermissionDenied()
      context = super(ProjectUpdate, self).get_context_data(**kwargs)
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": reverse("projects-list"), "label": "Projects" },
        {"url": reverse("projects-detail", args=[self.object.id]), "label": self.object.name },
        {"url": reverse("projects-edit", args=[self.object.id]), "label": "Edit" },
      )
      return context

#    def get_form(self, form_class=None):
#      form = super(ProjectUpdate, self).get_form(form_class)
#      if self.request.user.is_staff:
#        form.fields = self.fields_admin
#      return form
    def get_form_class(self):
      fields = self.fields_admin if self.request.user.is_staff else self.fields
      return model_forms.modelform_factory(self.model, fields=fields)

class JobDetail(DetailView):
    model = Job

    def get_object(self, queryset = None):
      obj = super(JobDetail, self).get_object(queryset)
      if self.request.user.is_staff: return obj
      if obj.project.public: return obj
      if obj.project.owner == self.request.user: return obj
      raise PermissionDenied()

    def get_context_data(self, **kwargs):
      context = super(JobDetail, self).get_context_data(**kwargs)
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": reverse("projects-list"), "label": "Projects" },
        {"url": reverse("projects-detail", args=[self.object.project.id]), "label": self.object.project.name },
        {"url": reverse("jobs-detail", args=[self.object.id]), "label": self.object.name },
      )
      kron = Kron(self.object.project.path)
      stat = kron.script_status(self.object.script_id)
      context["status"] = stat._asdict()
      return context


class JobForm(ModelForm):
    pipeline = model_forms.ChoiceField()
    dataset = model_forms.ChoiceField()

    class Meta:
      fields = ['name', 'description', 'pipeline', 'dataset']
      model = Job

    def __init__(self, project = None, *args, **kwargs):
      super(JobForm, self).__init__(*args, **kwargs)
#      if not project: project = Project.objects.get(pk=kwargs.pop("pk"))
#      project = kwargs.pop("project")
      datasets = project.datasets()
      pipelines = project.pipelines()
      ds = []

      for set in datasets:
        ds.append((set["name"], set["name"]))
      pp = []
      for pip in pipelines:
        pp.append((pip["name"], pip["name"]))

      self.fields["dataset"].choices = tuple(ds)
      self.fields["pipeline"].choices = tuple(pp)


class RunJobView(CreateView):
    model = Job
#    fields = ['name', 'description', 'pipeline', 'dataset']
    form_class = JobForm

    def get_form(self):
      return super(RunJobView, self).get_form()

    def get_form_kwargs(self):
      kwargs = super(RunJobView, self).get_form_kwargs()
      self.project = Project.objects.get(pk=self.kwargs.get("pk"))
      kwargs['project'] = self.project
      return kwargs

    def form_valid(self, form):
      self.object = form.save(False)
      self.object.owner = self.request.user
      self.object.project = Project.objects.get(pk=self.kwargs.get("pk"))
      try:
          kron = Kron(self.object.project.path)
          data = kron.start(self.object.pipeline, self.object.dataset)
          self.object.script_id = data.script_id
          messages.success(self.request, "Job started: {}".format(self.object.script_id))
      except:
          messages.error(self.request, "Unable to start job")
          return HttpResponseRedirect(self.get_success_url())
      self.object.save()
      return HttpResponseRedirect(self.get_success_url())
#      ret = super(RunJobView, self).form_valid(form)
#      return ret


    def get_context_data(self, **kwargs):
      context = super(RunJobView, self).get_context_data(**kwargs)
      project = Project.objects.get(pk=self.kwargs.get("pk"))
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": "/kron/", "label": "Projects" },
        {"url": reverse("projects-detail", args=[project.id]), "label": project.name },
        {"url": "", "label": "New job" },
      )
      return context

#    def get_form_class(self):
#      return model_forms.modelform_factory(self.model, fields=self.fields, form=JobForm)


@method_decorator(login_required, name='dispatch')
class DaemonStateView(TemplateView):
    template_name = 'kron/daemon_state.html'

    def get_context_data(self, **kwargs):
      context = super(DaemonStateView, self).get_context_data(**kwargs)
      context["breadcrumb"] = (
        {"url": "/",      "label": "MountainSort" },
        {"url": reverse("projects-list"), "label": "Projects" },
        {"url": "", "label": "Daemon State" },
      )
      state = subprocess.check_output(["/home/magland/dev/mountainlab/bin/mountainprocess", "daemon-state", "magland"])
      context["daemon_state"] = state
#      parser = json.JSONDecoder()
      context["state"] = json.loads(state.decode('utf-8'))
      return context


def static(request, page_name = None):
    context = {}
    context["page"] = "static/{}.html".format(page_name)
    return render(request, 'static.html', context)
