from django.conf.urls import url
from apps.users.views import UserInfoView, UploadImageView, ChangePwdView, MyCourseView, MyFavOrgView, MyFavTeacherView, \
    MyFavCourseView, MyMessageView, SendEmailCodeView,UpdateEmailView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name='info'),  # 个人中心主页
    url(r'^image/upload/$', UploadImageView.as_view(), name='image'),  # 头像上传
    url(r'^update/pwd/$', ChangePwdView.as_view(), name='update/pwd'),  # 修改密码
    # url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),  # 个人课程,由下面这条完全替代
    url(r'^mycourse/$',
        login_required(TemplateView.as_view(template_name='usercenter-mycourse.html'), login_url='/login/'),
        {'current_page': 'mycourse'}, name='mycourse'),
    url(r'^myfavorg/$', MyFavOrgView.as_view(), name='myfavorg'),
    url(r'^myfavteacher/$', MyFavTeacherView.as_view(), name='myfavteacher'),
    url(r'^myfav_course/$', MyFavCourseView.as_view(), name='myfav_course'),
    url(r'^messages/$', MyMessageView.as_view(), name='messages'),
    url(r'^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),  # 发送邮箱验证码
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),  # 修改邮箱
]
