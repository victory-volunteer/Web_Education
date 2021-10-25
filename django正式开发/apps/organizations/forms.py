from django import forms
from apps.operations.models import UserAsk
import re


class AddAskForm(forms.ModelForm):
    """
    自动生成form表单
    """
    # 手动添加覆盖
    mobile = forms.CharField(max_length=11, min_length=11, required=True)

    # 在这里设置required=True,而不是在models中设置，为了防止创建用户时出错

    class Meta:
        model = UserAsk  # 指定哪张表
        fields = ['name', 'mobile', 'course_name']  # 指定哪些字段

    def clean_mobile(self):
        """
        验证手机号码是否合法
        """
        mobile = self.cleaned_data['mobile']

        # regex_mobile = r"^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        # p = re.compile(regex_mobile)
        # if p.match(mobile):
        if re.match(r'^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$', mobile):
            return mobile
        else:
            raise forms.ValidationError('手机号码非法', code='mobile_invalid')
