from django.conf.urls import url
from django.views.generic import TemplateView

from apps.users.views import UserInfoView, UploadImageView, ChangePwdView

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name="info"),
    url(r'^image/upload/$', UploadImageView.as_view(), name="image"),
    url(r'^update/pwd/$', ChangePwdView.as_view(), name="update_pwd"),

]
