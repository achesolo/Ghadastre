from django.urls import path
from . views import homepageview, searchparcelgeneral, parceldetailview, parcelownerdetailview, \
    searchparcelbypoint, searchparcelbyfeaturetype

urlpatterns = [
    path(r'^', homepageview, name='homepage'),
    path('searchparcelgeneral/<str:term>', searchparcelgeneral, name="searchparcelgeneral"),
    path('searchparcelbypoint/<str:easting_longitude>/<str:northing_latitude>/<str:srid>',
         searchparcelbypoint, name="searchparcelbypoint"),
    path('searchparcelbyfeaturetype/<str:feature>/<str:srid>', searchparcelbyfeaturetype,
         name="searchparcelbyfeaturetype"),
    path('parceldetail/<str:code>', parceldetailview, name="parceldetail"),
    path('parcelownerdetail/<str:code>', parcelownerdetailview, name="parcelownerdetail"),
]