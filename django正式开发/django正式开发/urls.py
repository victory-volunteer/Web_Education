"""django正式开发 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import TemplateView
from apps.organizations.views import OrgView
from django.urls import path
from django.conf.urls import url, include
import xadmin
from apps.users.views import LoginView, LogoutView, RegisterView, ActiveUserView, ForgetPwdView,ResetView,ModifyPwdView
from django.views.static import serve
from django正式开发.settings import MEDIA_ROOT
from apps.operations.views import IndexView

urlpatterns = [
    # path('admin/', admin.site.urls),   # 有了xadmin就不需要admin了
    path('xadmin/', xadmin.site.urls),

    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),
    url('^reset/(?P<active_code>.*)/', ResetView.as_view(), name='reset_pwd'),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),

    # include用来指明路径和应用名,namespace为命名空间
    url(r'^org/', include(('apps.organizations.urls', 'organizations'), namespace='org')),
    url(r'^op/', include(('apps.operations.urls', 'operations'), namespace='op')),
    url(r'^course/', include(('apps.courses.urls', 'courses'), namespace='course')),
    url(r'^users/', include(('apps.users.urls', 'users'), namespace='users')),

    url(r'^captcha/', include('captcha.urls')),  # 添加图形验证码，url方式支持正则表达式
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    # 配置上传文件的访问url，'document_root'指明来哪个目录寻找，(?P<path>.*)分组起名path,供serve函数使用

    # url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]
# 全局404页面配置
handler404 = 'users.views.pag_not_found'
# 全局500页面配置
handler500 = 'users.views.page_error'
