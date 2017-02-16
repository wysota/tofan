from django.contrib import admin
from kron.models import Project, Job, Script

# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'public', 'path', 'created')
    list_filter = ('owner', 'public')
    search_fields = ('name', 'owner__username', 'owner__first_name', 'owner__last_name', 'path')

class JobAdmin(admin.ModelAdmin):
    list_display = ('name','project', 'owner', 'pipeline', 'dataset', 'created')
    list_filter = ('project','pipeline', 'dataset', 'owner')
    list_select_related = True
#    readonly_fields = ('project', 'owner',)
    search_fields = ('project__name', 'pipeline', 'dataset', 'owner__username', 'owner__first_name', 'owner__last_name')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Script)


admin.site.site_header = 'Mountainsort administration'
admin.site.site_title = 'Mountainsort administration'