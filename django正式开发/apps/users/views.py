from django.shortcuts import render
import re
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from apps.users.forms import LoginForm, RegisterGetForm, RegisterPostForm, UploadImageForm, UserInfoForm, ChangePwdForm, \
    ForgetPwdForm, ModifyPwdForm
from apps.users.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from pure_pagination import Paginator, PageNotAnInteger
from apps.operations.models import UserCourse
from apps.operations.models import UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Course
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from apps.utils.email_send import send_register_email
from apps.users.models import EmailVerifyRecord
from django.contrib.auth.hashers import make_password
from django.shortcuts import render_to_response
import datetime

TIME_REGISTER_AGE = ''


class CustomAuth(ModelBackend):
    """自定义用户django登录验证查询"""

    def authenticate(self, request, username=None, password=None, **kwargs):  # 此句话是固定的
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
            # 为了在输入用户名或电话号码或邮箱时都能够查询到用户
            if user.check_password(password):  # 将明文密码加密与数据库中密码比较看是否相同
                return user
        except Exception as e:
            return None


def message_nums(request):
    """为了所有页面都能显示未读消息数量，所以手动注入全局变量"""
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()
                }
    else:
        return {}


class MyMessageView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'message'
        messages = UserMessage.objects.filter(user=request.user)
        for message in messages:  # 只要用户点击进入我的消息，则变为已读
            message.has_read = True
            message.save()
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(messages, per_page=1, request=request)
        messages = p.page(page)
        return render(request, 'usercenter-message.html',
                      {'current_page': current_page, 'messages': messages})


class MyFavCourseView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'myfavcourse'
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            try:
                course = Course.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Course.DoesNotExist as e:  # 课程被删除的处理
                pass
        return render(request, 'usercenter-fav-course.html',
                      {'course_list': course_list, 'current_page': current_page})


class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'myfavteacher'
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html',
                      {'teacher_list': teacher_list, 'current_page': current_page})


class MyFavOrgView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'myfavorg'
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {'org_list': org_list, 'current_page': current_page})


class MyCourseView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'mycourse'
        # my_courses = UserCourse.objects.filter(user=request.user)
        # 注意：上面这句话也可以直接在html中传入user.usercourse_set.all来替代，user对象会自动注入到html中
        return render(request, 'usercenter-mycourse.html', {
            # 'my_courses': my_courses,
            'current_page': current_page
        })


class ChangePwdView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        """修改密码"""
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return JsonResponse({'status': 'fail', 'msg': '密码不一致'})
            # 以上三行可由ChangePwdForm中def clean(self)替代，但有问题
            user = request.user
            user.set_password(pwd1)
            user.save()
            login(request, user)  # 使修改密码后不退出登录
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse(pwd_form.errors)


class UploadImageView(LoginRequiredMixin, View):
    login_url = '/login/'

    # def save_file(self, file):
    #     with open('D:/django正式开发/media/head_image/uploaded.jpg', 'wb') as f:
    #         for chunk in file.chunks():
    #             f.write(chunk)
    def post(self, request, *args, **kwargs):
        """处理用户上传头像"""
        # 方法1：此方法只能将用户头像简单保存在本地，有许多细节无法处理
        # files = request.FILES['image']  # 注意要和html中name属性一致，此处都为image
        # self.save_file(files)
        # 方法2：使用ModelForm
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        # 上传的文件都在request.FILES里面获取，所以这里要多传一个这个参数
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail'})


class UserInfoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = 'info'
        captcha_form = RegisterGetForm()
        return render(request, 'usercenter-info.html', {'captcha_form': captcha_form, 'current_page': current_page})

    def post(self, request, *args, **kwargs):
        """保存个人信息"""
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse(user_info_form.errors)


class LogoutView(View):
    # 退出登录,导入logout模块
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class LoginView(View):
    """登录验证"""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # 检验用户是否登录
            return HttpResponseRedirect(reverse('index'))
        # 这样写，在登录状态下，即使指定url为/login/,也不会返回登录页面
        # 登录页面轮播图
        banners = Banner.objects.all()[:3]
        next = request.GET.get('next', '')
        return render(request, 'login.html', {'next': next, 'banners': banners})

    def post(self, request, *args, **kwargs):
        # 表单验证
        login_form = LoginForm(request.POST)  # (实例化)
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():  # 如果表单验证通过
            user_name = login_form.cleaned_data['username']  # cleaned_data用来读取forms.py中表单返回值
            password = login_form.cleaned_data['password']
            user = authenticate(username=user_name, password=password)  # 通过用户和密码查询用户是否存在
            if user is not None:
                if user.is_active:
                    print("邮箱已激活，成功登陆")
                    login(request, user)  # 登录到用户
                    # 登录成功之后应该怎么返回页面
                    next = request.GET.get('next', '')  # 取登录页面的参数
                    if next:
                        return HttpResponseRedirect(next)
                    return HttpResponseRedirect(reverse('index'))
                    # 使用HttpResponseRedirect返回首页后url才会改变，重定向url，使用reverse可以使用name字段
                else:
                    print('邮箱未激活，登录失败')
                    return render(request, 'login.html',
                                  {'msg': '邮箱未激活，登录失败', 'login_form': login_form, 'banners': banners})
            else:  # 未查询到用户
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form, 'banners': banners})
        else:
            return render(request, 'login.html', {'login_form': login_form, 'banners': banners})


class RegisterView(View):
    """用户注册"""

    def get(self, request, *args, **kwargs):
        banners = Banner.objects.all()[:3]
        register_get_form = RegisterGetForm()  # 实例化
        return render(request, 'register.html', {'register_get_form': register_get_form, 'banners': banners})

    def post(self, request, *args, **kwargs):
        banners = Banner.objects.all()[:3]
        register_post_form = RegisterPostForm(request.POST)
        if register_post_form.is_valid():
            email = register_post_form.cleaned_data['email']
            password = register_post_form.cleaned_data['password']
            user = UserProfile(username=email)  # 新建一个用户,username为必填字段
            user.set_password(password)  # 加密密码
            user.email = email
            # 默认添加的用户是激活状态（is_active=1表示True），这里修改默认的状态为 False，只有用户邮箱激活后才改为True
            user.is_active = False
            user.save()
            send_register_email(email, 'register')
            return HttpResponseRedirect(reverse('login'))
        else:
            register_get_form = RegisterGetForm()
            return render(request, 'register.html',
                          {'register_get_form': register_get_form, 'register_post_form': register_post_form,
                           'banners': banners})


class ForgetPwdView(View):
    def get(self, request, *args, **kwargs):
        banners = Banner.objects.all()[:3]
        forget_form = ForgetPwdForm()
        return render(request, 'forgetpwd.html', {'banners': banners, 'forget_form': forget_form})

    def post(self, request, *args, **kwargs):
        banners = Banner.objects.all()[:3]
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = forget_form.cleaned_data['email']
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form, 'banners': banners})


class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                if record.is_active:
                    record.is_active = False
                    record.save()
                    email = record.email
                    return render(request, "password_reset.html", {"email": email})
                else:
                    return render(request, 'email_active_fail.html')
        else:
            return render(request, "email_active_fail.html")


class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


class ActiveUserView(View):
    """
    激活邮件
    """

    def get(self, request, active_code):
        TIME_REGISTER_AGE = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 点击激活后的时间
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                create_time = re.match(r".*:.*:.{2}", str(record.send_time)).group()
                print("生成邮箱注册激活时:", create_time)
                print("点击邮箱注册激活时:", TIME_REGISTER_AGE)
                seconds = (datetime.datetime.strptime(TIME_REGISTER_AGE,
                                                      "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(
                    str(create_time), "%Y-%m-%d %H:%M:%S")).seconds
                if seconds >= 60:
                    record.is_active = False
                    record.save()
                    print("邮箱注册激活存在时间长达{}秒,已过期,状态改为：{}".format(seconds, record.is_active))
                    return render(request, "email_active_fail.html")
                if record.is_active:
                    # 获取到对应邮箱
                    email = record.email
                    # 查找到邮箱对应的 user
                    user = UserProfile.objects.get(email=email)
                    user.is_active = True
                    user.save()
                    record.is_active = False
                    record.save()
                    # 激活成功 登录到首页
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'email_active_fail.html')
        # 验证码不对的时候跳转到激活失败页面
        else:
            return render(request, 'email_active_fail.html')


class SendEmailCodeView(LoginRequiredMixin, View):
    """发送邮箱修改验证码"""
    login_url = '/login/'

    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return JsonResponse({"email": "邮箱已存在"})

        send_register_email(email, 'update_email')
        return JsonResponse({"status": "success"})


class UpdateEmailView(LoginRequiredMixin, View):
    '''修改邮箱'''
    login_url = '/login/'

    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"email": "验证码无效"})


def pag_not_found(request):
    # 全局404处理函数
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 全局500处理函数
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
