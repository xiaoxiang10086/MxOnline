from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import redis
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.utils.YunPian import send_single_sms
from apps.utils.random_str import generate_random
from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, UploadImageForm
from apps.users.forms import UserInfoForm, ChangePwdForm
from apps.users.forms import RegisterGetForm, RegisterPostForm, UpdateMobileForm
from MxOnline.settings import yp_apikey, REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile
from apps.operations.models import UserCourse

class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mycourse"
        # my_courses = UserCourse.objects.filter(user=request.user)
        
        return render(request, "usercenter-mycourse.html",{
            # "my_courses":my_courses,
            "current_page":current_page
        })

class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        mobile_form = UpdateMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            #已经存在的记录不能重复注册
            # if request.user.mobile == mobile:
            #     return JsonResponse({
            #         "mobile": "和当前号码一致"
            #     })
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({
                    "mobile":"该手机号码已经被占用"
                })
            user = request.user
            user.mobile = mobile
            user.username = mobile
            user.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(mobile_form.errors)
            # logout(request)

class ChangePwdView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            # pwd1 = request.POST.get("password1", "")
            # pwd2 = request.POST.get("password2", "")
            #
            # if pwd1 != pwd2:
            #     return JsonResponse({
            #         "status":"fail",
            #         "msg":"密码不一致"
            #     })
            pwd1 = request.POST.get("password1", "")
            user = request.user
            user.set_password(pwd1)
            user.save()
            # login(request, user)

            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(pwd_form.errors)

class UploadImageView(LoginRequiredMixin, View):
    login_url = "/login/"

    # def save_file(self, file):
    #     with open("C:/Users/Administrator/PycharmProjects/MxOnline/media/head_image/uploaded.jpg", "wb") as f:
    #         for chunk in file.chunks():
    #             f.write(chunk)


    def post(self, request, *args, **kwargs):
        #处理用户上传的头像
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse({
                "status": "fail"
            })

        # files = request.FILES["image"]
        # self.save_file(files)

        #1. 如果同一个文件上传多次，相同名称的文件应该如何处理
        #2. 文件的保存路径应该写入到user
        #3. 还没有做表单验证

class UserInfoView(LoginRequiredMixin, View):

    login_url = "/login/"
    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        return render(request, "usercenter-info.html", {
            "captcha_form":captcha_form,
            "current_page":current_page
        })

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(user_info_form.errors)

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        return render(request, "register.html", {
            "register_get_form":register_get_form
        })
    
    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        if register_post_form.is_valid():
            mobile = register_post_form.cleaned_data["mobile"]
            password = register_post_form.cleaned_data["password"]
            # 新建一个用户
            user = UserProfile(username=mobile)
            user.set_password(password)
            user.mobile = mobile
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            register_get_form = RegisterGetForm()
            return render(request, "register.html", {
                "register_get_form":register_get_form,
                "register_post_form": register_post_form
            })

class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
        })

    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        if login_form.is_valid():
            #没有注册账号依然可以登录
            mobile = login_form.cleaned_data["mobile"]
            existed_users = UserProfile.objects.filter(mobile=mobile)
            if existed_users:
                user = existed_users[0]
            else:
                #新建一个用户
                user = UserProfile(username=mobile)
                password = generate_random(10, 2)
                user.set_password(password)     #进行加密
                user.mobile = mobile
                user.save()
            login(request, user)
            next = request.GET.get("next", "")
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse("index"))
        else:
            d_form = DynamicLoginForm()
            return render(request, "login.html", {"login_form": login_form,
                                                  "d_form": d_form,
                                                  "dynamic_login":dynamic_login})


class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)
        re_dict = {}
        if send_sms_form.is_valid():
            mobile = send_sms_form.cleaned_data["mobile"]
            #随机生成数字验证码
            code = generate_random(4, 0)
            re_json = send_single_sms(yp_apikey,code ,mobile=mobile)
            if re_json["code"] == 0:
                re_dict["status"] = "success"
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
                r.set(str(mobile), code)
                print("验证码：", code)
                r.expire(str(mobile), 60*5) #设置验证码五分钟过期
            else:
                re_dict["msg"] = re_json["msg"]
        else:
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)
        
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
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
        })
         
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
