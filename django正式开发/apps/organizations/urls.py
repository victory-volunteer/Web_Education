from django.conf.urls import url
from apps.organizations.views import OrgView, AddAskView, OrgHomeView, OrgTeacherView, OrgCourseView, OrgDescView,TeacherListView,TeacherDetailView
from django.urls import path

urlpatterns = [
    url(r'^list/$', OrgView.as_view(), name='list'),
    url(r'^add_ask/$', AddAskView.as_view(), name='add_ask'),
    url(r'^(?P<org_id>\d+)/desc/$', OrgDescView.as_view(), name='desc'),
    url(r'^(?P<org_id>\d+)/course/$', OrgCourseView.as_view(), name='course'),
    url(r'^(?P<org_id>\d+)/teacher/$', OrgTeacherView.as_view(), name='teacher'),
    url(r'^(?P<org_id>\d+)/$', OrgHomeView.as_view(), name='home'),
    # path('<int:org_id>/', OrgHomeView.as_view(), name='home'),  # 此中方法也可以，推荐使用上面那一种
    url(r'^teachers/$', TeacherListView.as_view(), name='teachers'),
    url(r'^teachers/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name='teachers_detail'),

]
