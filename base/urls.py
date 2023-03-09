from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("", views.index, name='index'),
    re_path(r'^explore/(\d{6})/$', views.explore, name='explore'),

    re_path(r'^getNeighbourhood/(\d{6})/(\d+)/(\d+)/$',views.getNeighbourhood_ajax,name='neighbourhood'),
    re_path(r'^getNeighbourhood/(\d{6})/$',views.getNeighbourhood_ajax,name='neighbourhood'),
    re_path(r'^getNeighbourhood/$',views.getNeighbourhood_ajax,name='neighbourhood'),

    re_path(r'^fillNetwork/(\w+)$',csrf_exempt(views.fillNetwork_ajax),name='fillnetwork'),
    re_path(r'^fillNetwork/$',csrf_exempt(views.fillNetwork_ajax),name='fillnetwork'),

    re_path(r'^details/(\d{6})/$', views.getDetails_ajax, name='details'),
    re_path(r'^score/(\d{6})/(\d{6})/$', views.score, name='score'),
    re_path(r'^error/$', views.error, name='error'),
    re_path(r'^disclaimer/$', views.disclaimer, name='disclaimer'),
    re_path(r'^get_entities/$', views.get_entities, name='get_entities'),
    #get the table.
    re_path(r'^table/(\d{6})/$', views.getTable, name='table'),
    re_path(r'^downloadTable/(\d{6})/$', views.download_table, name='download_table'),
]
