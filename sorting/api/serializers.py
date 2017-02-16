from django.contrib.auth.models import User
from kron.models import Project, Job, Script
from rest_framework import serializers

class KeyValueSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=200)

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    pipelines = KeyValueSerializer(many=True, read_only=True)
    datasets = KeyValueSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = ('url', 'id', 'owner', 'public', 'name', 'description', 'created', 'path', 'pipelines', 'datasets')

class JobSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.StringRelatedField()
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Job
        fields = ('url', 'id', 'owner', 'name', 'description', 'project', 'created', 'pipeline', 'dataset')

class ScriptSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())

    class Meta:
        model = Script
        fields = ('url', 'id', 'name', 'job')

