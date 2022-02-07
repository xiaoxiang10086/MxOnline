from django.conf.urls import url
from apps.courses.views import CourseListView

urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name="list"),
]
