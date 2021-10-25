from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser  # 用于继承django创建的原有auth_user表

GENDER_CHOICES = {
    ('male', '男'),
    ('female', '女')
}


class BaseModel(models.Model):
    """用来被其他类继承(users作为底层应用可以被其他应用继承，因此BaseModel放在users的models下)"""
    add_time = models.DateTimeField(default=datetime.now, verbose_name='实体生成时间')

    # 写为datetime.now()，将来的时间就是编译时间；若写为datetime.now,django会自动调用，将来就是实例化时的时间

    class Meta:
        abstract = True  # 防止BaseModel类生成一张表


class UserProfile(AbstractUser):
    """补充原有auth_user表没有的额外字段"""
    nick_name = models.CharField(max_length=50, verbose_name='昵称', default='')
    birthday = models.DateField(verbose_name='生日', null=True, blank=True)
    gender = models.CharField(verbose_name='性别', choices=GENDER_CHOICES, max_length=6)  # 6为female的长度
    address = models.CharField(max_length=100, verbose_name='地址', default='')
    mobile = models.CharField(max_length=11, verbose_name='电话号码')
    # unique=True代表不同用户之间不允许重复，要将这里的unique=True去掉，否则在添加用户时会出错，保证电话号码唯一的操作可以在form表单验证时进行
    image = models.ImageField(verbose_name='头像', upload_to='head_image/%Y/%m', default='upimg/default.png', null=True,
                              blank=True)

    # upload_to='head_image/%Y/%m'代表django会将用户头像上传到/media/head_image下，并标明日期

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    # def unread_nums(self):
    #     """显示未读消息数量，已由users/views下的message_nums方法替代"""
    #     return self.usermessage_set.filter(has_read=False).count()

    def __str__(self):
        """用于在后台显示，使打印出来的结果更人性化"""
        if self.nick_name:
            return self.nick_name
        else:
            return self.username


class EmailVerifyRecord(models.Model):
    """
    图形验证码
    """
    send_choices = (
        ('register', '注册'),
        ('forget', '找回密码'),
        ('update_email', '修改邮箱')
    )

    code = models.CharField(verbose_name='验证码', max_length=20)
    email = models.EmailField(verbose_name='邮箱', max_length=50)
    send_type = models.CharField(choices=send_choices, max_length=25)
    send_time = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name
