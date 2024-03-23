from django.urls import path, re_path, include
from rest_framework import routers
from courses import views
from ecourseapiv2.urls import schema_view

r = routers.DefaultRouter()
r.register('categories', views.CategoryViewset, basename='categories')
r.register('courses', views.CourseViewset, basename='courses')
r.register('lessons', views.LessonViewset, basename='lessons')
r.register('users', views.UserViewset, basename='users')

urlpatterns = [
    path('', include(r.urls))
]
