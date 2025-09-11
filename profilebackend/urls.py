from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path("", views.get_employee_profile, name="get_employee_profile"),
    path("file/<str:file_id>/", views.serve_file, name="serve_file"),
    path("update-image/", views.update_profile_image, name="update_profile_image"),
    path("update/", views.update_employee_profile, name="update_employee_profile"),
    path("change-password/", views.change_password, name="change_password"),

]
