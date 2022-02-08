from django.conf.urls import url
from django.views.generic import TemplateView

from apps.users.views import UserInfoView

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name="info"),
]
