# -*- coding = utf-8 -*-
# @Time : 2020/8/9 10:06
# @File : adminx.py
# @Software : PyCharm
import xadmin
from apps.courses.models import Course, Lesson, Video, CourseResource, CourseTag, BannerCourse


class GlobalSettings(object):
    site_title = '慕课后台管理系统'
    site_footer = '慕课在线网'
    # menu_style = 'accordion'  # 用于将xadmin侧边栏收起来


class BaseSettings(object):
    """添加主题功能（选择不同皮肤）"""
    enable_themes = True
    use_bootswatch = True


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_editable = ['desc', 'degree']

    def queryset(self):
        qs = super().queryset()
        qs = qs.filter(is_banner=True)
        return qs


class CourseAdmin(object):
    list_display = ['name', 'desc', 'show_image', 'go_to', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_editable = ['desc', 'degree']
    ordering = ['-click_nums']                  # 按照点击数来排倒序
    readonly_fields = ['students', 'add_time']  # 在编辑页面时设置只读字段，只能看
    exclude = ['click_nums', 'fav_nums']        # 在编辑页面时设置去除的字段，不显示
    # 注意：必填字段不能配置到readonly_fields和exclude中来，且exclude中的字段不能在其他限制里出现，因为exclude里是要去除的

    def queryset(self):  # 定义可以返回哪些数据
        qs = super().queryset()  # 得到默认返回的所有数据
        if not self.request.user.is_superuser:  # 若是不是超级管理员则返回部分数据
            qs = qs.filter(teacher=self.request.user.teacher)
            # 因为teacher和用户是一对一的关系，可以直接用当前用户反向取teacher
        return qs



class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']  # course__name代表对课程course(外键)上的name字段中过滤


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'file', 'add_time']
    search_fields = ['course', 'name', 'file']
    list_filter = ['course', 'name', 'file', 'add_time']


class CourseTagAdmin(object):
    list_display = ['course', 'tag', 'add_time']
    search_fields = ['course', 'tag']
    list_filter = ['course', 'tag', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)
xadmin.site.register(xadmin.views.BaseAdminView, BaseSettings)
xadmin.site.register(CourseTag, CourseTagAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
