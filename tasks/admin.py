from django.contrib import admin
from tasks.models import Task

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)


# Register your models here.

admin.site.register(Task, TaskAdmin)