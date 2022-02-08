from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from apps.users.views import UserInfoView, UploadImageView, ChangePwdView, ChangeMobileView

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name="info"),
    url(r'^image/upload/$', UploadImageView.as_view(), name="image"),
    url(r'^update/pwd/$', ChangePwdView.as_view(), name="update_pwd"),
    url(r'^update/mobile/$', ChangeMobileView.as_view(), name="update_mobile"),

    # url(r'^mycourse/$', MyCourseView.as_view(), name="mycourse"),
    url(r'^mycourse/$', login_required(TemplateView.as_view(template_name="usercenter-mycourse.html"), 
                                        login_url="/login/"),
                                        {"current_page":"mycourse"}, 
                                        name="mycourse"),
]
