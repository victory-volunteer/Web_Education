from django.shortcuts import render
from django.views import View
from apps.operations.models import UserFavorite, CourseComments, Banner
from apps.operations.forms import UserFavForm, CommentsForm
from apps.courses.models import Course
from apps.organizations.models import CourseOrg, Teacher
from django.http import JsonResponse


class IndexView(View):
    def get(self, request, *args, **kwargs):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
        banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html',
                      {'banners': banners, 'banner_courses': banner_courses, 'course_orgs': course_orgs,
                       'courses': courses})


class CommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # 先判断用户是否登录
            return JsonResponse({'status': 'fail', 'msg': '用户未登录'})
        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            course = comment_form.cleaned_data['course']
            comments = comment_form.cleaned_data['comments']
            comment = CourseComments()
            comment.user = request.user
            comment.comments = comments
            comment.course = course
            comment.save()
            return JsonResponse({'status': 'success', })
        else:
            return JsonResponse({'status': 'fail', 'msg': '参数错误'})


class AddFavView(View):
    def post(self, request, *args, **kwargs):
        """用户收藏与取消收藏操作，用户必须登录后才可以收藏"""
        if not request.user.is_authenticated:  # 先判断用户是否登录
            return JsonResponse({'status': 'fail', 'msg': '用户未登录'})
        user_fav_form = UserFavForm(request.POST)
        if user_fav_form.is_valid():
            fav_id = user_fav_form.cleaned_data['fav_id']
            fav_type = user_fav_form.cleaned_data['fav_type']
            # 查看当前用户是否收藏
            existed_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
            if existed_records:
                existed_records.delete()  # 若收藏后再次点击，则会取消收藏
                if fav_type == 1:
                    course = Course.objects.get(id=fav_id)
                    if course.fav_nums > 0:
                        course.fav_nums -= 1
                        course.save()
                elif fav_type == 2:
                    course_org = CourseOrg.objects.get(id=fav_id)
                    if course_org.fav_nums > 0:
                        course_org.fav_nums -= 1
                        course_org.save()
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    if teacher.fav_nums > 0:
                        teacher.fav_nums -= 1
                        teacher.save()
                return JsonResponse({'status': 'success', 'msg': '收藏'})
            else:
                user_fav = UserFavorite()
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.user = request.user
                user_fav.save()
                if fav_type == 1:
                    course = Course.objects.get(id=fav_id)
                    course.fav_nums += 1
                    course.save()
                elif fav_type == 2:
                    course_org = CourseOrg.objects.get(id=fav_id)
                    course_org.fav_nums += 1
                    course_org.save()
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums += 1
                    teacher.save()
                return JsonResponse({'status': 'success', 'msg': '已收藏'})
        else:
            return JsonResponse({'status': 'fail', 'msg': '参数错误'})
