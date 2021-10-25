from django.shortcuts import render
from django.views.generic.base import View
from apps.organizations.models import City, CourseOrg, Teacher
from pure_pagination import Paginator, PageNotAnInteger
from apps.organizations.forms import AddAskForm
from django.http import JsonResponse
from apps.operations.models import UserFavorite
from django.db.models import Q


class TeacherDetailView(View):
    def get(self, request, teacher_id, *args, **kwargs):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher_fav = False
        org_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                teacher_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                org_fav = True
        hot_teachers = Teacher.objects.all().order_by('-click_nums')[:3]

        return render(request, 'teacher-detail.html',
                      {'teacher': teacher, 'teacher_fav': teacher_fav, 'org_fav': org_fav,
                       'hot_teachers': hot_teachers})


class TeacherListView(View):
    def get(self, request, *args, **kwargs):
        all_teachers = Teacher.objects.all()
        teacher_nums = all_teachers.count()
        hot_teachers = Teacher.objects.all().order_by('-click_nums')[:3]
        # 搜索关键词
        keywords = request.GET.get('keywords', '')
        s_type = 'teacher'
        if keywords:
            all_teachers = all_teachers.filter(name__icontains=keywords)
        # 排序
        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = all_teachers.order_by('-click_nums')
        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers, per_page=2, request=request)
        teachers = p.page(page)

        return render(request, 'teachers-list.html',
                      {'teachers': teachers, 'teacher_nums': teacher_nums, 'sort': sort, 'hot_teachers': hot_teachers,
                       'keywords': keywords,
                       's_type': s_type})


class OrgDescView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated:  # 为了在刷新页面时不出错
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html',
                      {'course_org': course_org, 'current_page': current_page, 'has_fav': has_fav})


class OrgCourseView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()
        # 对机构课程数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, per_page=5, request=request)
        courses = p.page(page)
        return render(request, 'org-detail-course.html',
                      {'all_courses': courses, 'course_org': course_org, 'current_page': current_page,
                       'has_fav': has_fav})


class OrgTeacherView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teacher = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html',
                      {'all_teacher': all_teacher, 'course_org': course_org, 'current_page': current_page,
                       'has_fav': has_fav})


class OrgHomeView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teacher = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html',
                      {'all_courses': all_courses, 'all_teacher': all_teacher, 'course_org': course_org,
                       'current_page': current_page, 'has_fav': has_fav})


class AddAskView(View):
    """
    处理用户咨询
    """

    def post(self, request, *args, **kwargs):
        userask_form = AddAskForm(request.POST)
        if userask_form.is_valid():
            userask_form.save(commit=True)
            # 这个方法会返回AddAskForm实例,commit=True表示会提交给数据库并立即执行
            return JsonResponse({"status": "success"})
            # JsonResponse用来通过后台返回给前台数据，它会自动转为json
        else:
            return JsonResponse({"status": "fail", "msg": "添加出错"})


class OrgView(View):
    def get(self, request, *args, **kwargs):
        all_orgs = CourseOrg.objects.all()
        all_citys = City.objects.all()
        hot_orgs = all_orgs.order_by('-click_nums')[:3]  # 按点击数排序取前3
        # 搜索关键词
        keywords = request.GET.get('keywords', '')
        s_type = 'org'
        if keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=keywords) | Q(desc__icontains=keywords))
        # 通过机构类别对课程机构筛选
        category = request.GET.get('ct', '')  # 这里的ct要和html中ct一致，默认为空
        if category:
            all_orgs = all_orgs.filter(category=category)
        # 通过所在城市对课程机构筛选
        city_id = request.GET.get('city', '')  # 这里的ct要和html中ct一致，默认为空
        if city_id:
            if city_id.isdigit():  # 如果字符串只包含数字则返回 True 否则返回 False,
                # 若没有这句话，当用户输入非数字时，转int时会出错。int()只能转化由纯数字组成的字符串
                all_orgs = all_orgs.filter(city_id=int(city_id))
        # 对机构排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_orgs = all_orgs.order_by('-students')  # -students代表倒序，students代表顺序
        elif sort == 'courses':
            all_orgs = all_orgs.order_by('-course_nums')
        org_nums = all_orgs.count()  # 查询一共有多少数据
        # 对课程机构数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_orgs, per_page=5, request=request)
        # per_page=5表示每一页显示5条数据
        orgs = p.page(page)
        return render(request, 'org-list.html',
                      {'all_orgs': orgs, 'org_nums': org_nums, 'all_citys': all_citys, 'category': category,
                       'city_id': city_id, 'sort': sort, 'hot_orgs': hot_orgs, 'keywords': keywords,
                       's_type': s_type})
