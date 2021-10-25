from django.shortcuts import render
from django.views.generic.base import View
from apps.courses.models import Course, CourseTag, CourseResource,Video
from pure_pagination import Paginator, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.operations.models import UserFavorite, UserCourse, CourseComments


class CourseCommentsView(LoginRequiredMixin, View):
    login_url = '/login/'  # 表示当前类下的语句都必须在登录状态下才会显示，否则跳转到登录界面

    def get(self, request, course_id, *args, **kwargs):
        """课程章节详情"""
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()
        comments = CourseComments.objects.filter(course=course)
        # 查询用户是否已经关联了改课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            course.students += 1
            course.save()
        # 课程资源
        course_resources = CourseResource.objects.filter(course=course)
        # 学习过该课程的所有同学还学过
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by('-course__click_nums')[:5]
        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:  # 这句话也可以在上方.order_by前加.exclude(course__id=course.id)来替代
                related_courses.append(item.course)

        return render(request, 'course-comment.html',
                      {'course': course, 'course_resources': course_resources, 'related_courses': related_courses,
                       'comments': comments})


class CourseLessonView(LoginRequiredMixin, View):
    login_url = '/login/'  # 表示当前类下的语句都必须在登录状态下才会显示，否则跳转到登录界面

    def get(self, request, course_id, *args, **kwargs):
        """课程章节详情"""
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()
        # 查询用户是否已经关联了改课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            course.students += 1
            course.save()
        # 课程资源
        course_resources = CourseResource.objects.filter(course=course)
        # 学习过该课程的所有同学还学过
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by('-course__click_nums')[:5]
        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:  # 这句话也可以在上方.order_by前加.exclude(course__id=course.id)来替代
                related_courses.append(item.course)

        return render(request, 'course-video.html',
                      {'course': course, 'course_resources': course_resources, 'related_courses': related_courses})


class CourseDetailView(View):
    def get(self, request, course_id, *args, **kwargs):
        """课程详情"""
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()
        # 获取收藏状态
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        # 通过课程的tag做课程推荐

        # 此方法只适用于课程只有一个标签
        # tag = course.tag
        # related_courses = []
        # if tag:
        #     related_courses = Course.objects.filter(tag=tag).exclude(id=course.id)[:3]
        #     # 当前为排除id=course.id的，exclude(id__in=[course.id])用来排除id=列表内的值。

        # 此方法适用于课程有多个标签
        tags = course.coursetag_set.all()  # 返回一个可遍历的对象
        # tag_list = []
        # for tag in tags:
        #     tag_list.append(tag.tag)
        tag_list = [tag.tag for tag in tags]  # 等价于上面三行
        course_tags = CourseTag.objects.filter(tag__in=tag_list).exclude(course__id=course.id)
        related_courses = set()  # 由于一个课程有多个标签，所有可能展示的课程会重复，因此可以用set()去重
        for course_tag in course_tags:
            related_courses.add(course_tag.course)
            # course_tag.course就是取出xadmin页面中course属性对应的值,同时转为Course对象

        return render(request, 'course-detail.html',
                      {'course': course, 'has_fav_course': has_fav_course, 'has_fav_org': has_fav_org,
                       'related_courses': related_courses})


class CourseListView(View):
    def get(self, request, *args, **kwargs):
        """获取课程列表信息"""
        all_courses = Course.objects.order_by('-add_time')
        hot_courses = Course.objects.order_by('-click_nums')[:3]
        # 搜索关键词
        keywords = request.GET.get('keywords', '')
        s_type = 'course'
        if keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=keywords) | Q(desc__icontains=keywords) | Q(detail__icontains=keywords))
            # i表示忽略大小写,__contains表示拼凑为like语句，要想支持多种查询，就用Q,多个Q之间支持or操作
        # 排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, per_page=3, request=request)
        courses = p.page(page)
        return render(request, 'course-list.html',
                      {'all_courses': courses, 'sort': sort, 'hot_courses': hot_courses, 'keywords': keywords,
                       's_type': s_type})


class VideoPlayView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, course_id, video_id, *args, **kwargs):
        """课程视频播放"""

        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()
        video=Video.objects.get(id=int(video_id))
        # 查询用户是否已经关联了改课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            course.students += 1
            course.save()
        # 课程资源
        course_resources = CourseResource.objects.filter(course=course)
        # 学习过该课程的所有同学还学过
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by('-course__click_nums')[:5]
        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:  # 这句话也可以在上方.order_by前加.exclude(course__id=course.id)来替代
                related_courses.append(item.course)

        return render(request, 'course-play.html',
                      {'course': course, 'course_resources': course_resources, 'related_courses': related_courses,'video':video})
