from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-users/delete/<int:id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-jobs/', views.admin_jobs, name='admin_jobs'),
    path('admin-applications/', views.admin_applications, name='admin_applications'),
    path('post-job/', views.post_job, name='post_job'),
    path('delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('save-job/<int:id>/', views.save_job, name='save_job'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('apply/<int:id>/', views.apply_job, name='apply_job'),
]
