from django.contrib import admin
from .models import Application, Job, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'salary', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('title', 'description', 'employer__username')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('job__title', 'applicant__username')


admin.site.site_header = "Job Portal Admin"
admin.site.site_title = "Job Portal Admin"
admin.site.index_title = "Platform Overview"
