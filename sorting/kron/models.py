from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.safestring import mark_safe

import markdown

from sorting.settings import MOUNTAINSORT_SETTINGS

# Create your models here.
class Project(models.Model):
  owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='projects')
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True,default="", help_text='Supports markdown')
  created = models.DateTimeField(auto_now_add=True)
  path = models.CharField(max_length=200, default='')
  public = models.BooleanField(default=False)

  def __str__(self): 
    return self.name

  def absolutePath(self):
    bd = MOUNTAINSORT_SETTINGS["BASE_DIR"]
    return "{}/{}".format(bd, self.path)

  def pipelines(self):
    try:
     with open("{}/pipelines.txt".format(self.absolutePath())) as f:
      for line in f:
        tokens = line.split(" ",1)
        yield {'name': tokens[0], 'value': tokens[1] }
    except:
      return None

  def datasets(self):
   try:
    with open("{}/datasets.txt".format(self.absolutePath())) as f:
      for line in f:
        tokens = line.split(" ",1)
        yield {'name': tokens[0], 'value': tokens[1] }
   except:
    return None
    
  def run(self, owner):
    job = Job(name='example run', project=self, pipeline='p1', dataset='s1', owner = owner)
    job.save()
    return job

  def get_absolute_url(self):
    from django.urls import reverse
    return reverse('projects-detail', args=[str(self.id)])

  def description_markdown(self):
    return mark_safe(markdown.markdown(self.description, safe_mode='escape'))

class Job(models.Model):
  owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='jobs')
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='jobs')
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True, default="")
  created = models.DateTimeField(auto_now_add=True)
  pipeline = models.CharField(max_length=100)
  dataset = models.CharField(max_length=100)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    from django.urls import reverse
    return reverse('jobs-detail', args=[str(self.id)])

@receiver(models.signals.post_delete, sender=User)
def delete_owner(instance, **kwargs):
  jobs = Job.objects.all()
  for job in jobs:
    if not job.owner:
      job.owner = job.project.owner
      job.save()

class Script(models.Model):
  script_id = models.CharField(max_length=16, default='')
  name = models.CharField(max_length=200)
  job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='scripts')
  
  def __str__(self):
    return self.name


  