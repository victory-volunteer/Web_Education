# -*- coding = utf-8 -*-
# @Time : 2020/8/12 16:30
# @File : forms.py
# @Software : PyCharm
from django import forms
from captcha.fields import CaptchaField
from apps.users.models import UserProfile


class ChangePwdForm(forms.Form):
    """修改密码，由于密码在auth_user表内，所有要自己定义"""
    password1 = forms.CharField(required=True, min_length=6)
    password2 = forms.CharField(required=True, min_length=6)

    # def clean(self):  # 有问题待解决E:\django视频\待办\个人中心修改密码和手机号码.mp4:14分
    #     pwd1 = self.cleaned_data['password1']
    #     pwd2 = self.cleaned_data['password2']
    #     if pwd1 != pwd2:
    #         raise forms.ValidationError('密码不一致')  # 需要修改deco-user.js
    #     return self.cleaned_data


class UserInfoForm(forms.ModelForm):
    """个人中心保存"""

    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birthday', 'address']


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class LoginForm(forms.Form):
    username = forms.CharField(required=True, min_length=2)
    # required=True表示必填字段
    password = forms.CharField(required=True, min_length=3)
    # 这两个值必须和前端中的name属性相同


class RegisterGetForm(forms.Form):
    # 动态验证码注册
    captcha = CaptchaField()


class RegisterPostForm(forms.Form):
    # 邮箱注册
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=3)
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

    def clean_email(self):
        email = self.data.get('email')
        # 验证邮箱是否注册
        users = UserProfile.objects.filter(email=email)
        if users:
            raise forms.ValidationError('该邮箱已经注册')  # 抛出异常
        return email


class ForgetPwdForm(forms.Form):
    # 忘记密码
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    # 密码重置
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)
