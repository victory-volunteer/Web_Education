from django.db import models
from django.contrib.auth import get_user_model
from apps.users.models import BaseModel
from apps.courses.models import Course

UserProfile = get_user_model()
# 由于UserProfile覆盖了django自带的auth_user表，这样写可以知道使用的是哪个class，若后续直接使用django内部的auth_user也没有问题


class UserAsk(BaseModel):
    """用户不用必须登录才能提交查询信息，所以不需要指定外键"""
    name = models.CharField(max_length=20, verbose_name='姓名')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    course_name = models.CharField(max_length=50, verbose_name='课程名')

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{name}_{course} ({mobile})'.format(name=self.name, course=self.course_name, mobile=self.mobile)


class Banner(BaseModel):
    """首页轮播图"""
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banner/%Y/%m', max_length=200, verbose_name='轮播图')
    url = models.URLField(max_length=200, verbose_name='访问地址')
    index = models.IntegerField(default=0, verbose_name='轮播图顺序')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class CourseComments(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    comments = models.CharField(max_length=200, verbose_name='评论内容')

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.comments


class UserFavorite(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    fav_id = models.IntegerField(verbose_name='数据id')
    fav_type = models.IntegerField(choices=((1, '课程'), (2, '课程机构'), (3, '讲师')), default=1, verbose_name='收藏类型')
    # 由于后期收藏类型越来越多，外键也越来越多,此用来防止频繁修改表结构

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{user}_{id}'.format(user=self.user.username, id=self.fav_id)


class UserMessage(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    message = models.CharField(max_length=200, verbose_name='消息内容')
    has_read = models.BooleanField(default=False, verbose_name='是否已读')  # fasle表示未读

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.message


class UserCourse(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')

    class Meta:
        verbose_name = '用户课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.course.name
