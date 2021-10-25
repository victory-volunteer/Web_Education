from django.db import models
from apps.users.models import BaseModel
from apps.users.models import UserProfile


class City(BaseModel):
    """由于城市有许多，添加不方便，因此通过开一个城市表通过外键解决"""
    name = models.CharField(max_length=20, verbose_name=u'城市名')
    desc = models.CharField(max_length=200, verbose_name=u'描述')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseOrg(BaseModel):
    name = models.CharField(max_length=50, verbose_name='机构名称')
    desc = models.TextField(verbose_name='描述')
    tag = models.CharField(default='全国知名', max_length=10, verbose_name='机构标签')
    category = models.CharField(default='pxjg', verbose_name='机构类别', max_length=4,
                                choices=(('pxjg', '培训机构'), ('gr', '个人'), ('gx', '高校')))
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    image = models.ImageField(upload_to='org/%Y/%m', verbose_name=u'logo', max_length=100)
    address = models.CharField(max_length=150, verbose_name='机构地址')
    students = models.IntegerField(default=0, verbose_name='学习人数')
    course_nums = models.IntegerField(default=0, verbose_name='课程数')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='所在城市')
    is_auth = models.BooleanField(default=False, verbose_name='是否认证')
    is_gold = models.BooleanField(default=False, verbose_name='是否金牌')

    def courses(self):
        # 方法一
        # from apps.courses.models import Course   # 只可以写在这个方法里，在调用时才导入，否则报错
        # courses = Course.objects.filter(course_org=self)
        # 方法二：避免调用import
        courses = self.course_set.filter(is_classics=True)[:3]
        # 这里的course就是方法一里import的类名，只有当前类名是方法一里import的类名的外键，才可以这样反向取
        return courses

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Teacher(BaseModel):
    user = models.OneToOneField(UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='用户')   # 建立一对一的关系，一个用户对应一个讲师,使讲师成为单独的用户
    org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name='所属机构')
    name = models.CharField(max_length=50, verbose_name='教师名称')
    work_years = models.IntegerField(default=0, verbose_name='工作年限')
    work_company = models.CharField(max_length=50, verbose_name='就职公司')
    work_position = models.CharField(max_length=50, verbose_name='公司职位')
    points = models.CharField(max_length=50, verbose_name='教学特点')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    age = models.IntegerField(default=18, verbose_name='年龄')
    image = models.ImageField(upload_to='teacher/%Y/%m', verbose_name='头像', max_length=100)

    class Meta:
        verbose_name = '讲师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def course_nums(self):
        return self.course_set.all().count()
