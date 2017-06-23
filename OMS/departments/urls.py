from django.conf.urls import patterns, url
from departments import views


urlpatterns = patterns('',
                       # dep
                       url(r'^department_add/', views.department_add, name='department_add'),
                       url(r'^department_del/', views.department_del, name='department_del'),
                       url(r'^department_edit/(?P<pk>\d+)$', views.department_edit, name='department_edit'),
                       url(r'^department_list/', views.department_list, name='department_list'),
                       url(r'^department_detail/(?P<pk>\d+)$', views.department_detail, name='department_detail'),
#                       url(r'^department_search/$', views.department_search, name='department_search'),
                       )
