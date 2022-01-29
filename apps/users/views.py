from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from apps.users.forms import LoginForm, DynamicLoginForm

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))

class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html")
         
    def post(self, request, *args, **kwargs):
        #表单验证
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #用于通过用户和密码查询用户是否存在
            user_name = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=user_name, password=password)
            #1. 通过用户名查询到用户
            #2. 需要先加密再通过加密之后的密码查询
            # user = UserProfile.objects.get(username=user_name, password=password)
            if user is not None:
                #查询到用户
                login(request, user)
                #登录成功之后应该怎么返回页面
                next = request.GET.get("next", "")
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse("index"))
            else:
                #未查询到用户
                return render(request, "login.html", {"msg":"用户名或密码错误", "login_form": login_form})
        else:
            return render(request, "login.html", {"login_form": login_form})
