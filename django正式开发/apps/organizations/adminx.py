
import xadmin
from apps.organizations.models import Teacher, CourseOrg, City


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']


class CityAdmin(object):
    list_display = ['id', 'name', 'desc']       # 定义在列表页显示的字段
    search_fields = ['name', 'desc']            # 设置搜索框可以使用哪些字段进行搜索
    list_filter = ['name', 'desc', 'add_time']  # 设置过滤器可以使用哪些字段进行过滤
    list_editable = ['name', 'desc']            # 设置指定字段可以在列表页中直接进行编辑


xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)
