from django.urls import path
from . views import homepageview, searchparcelgeneral, parceldetailview, parcelownerdetailview, \
    searchparcelbypoint, searchparcelbyfeaturetype, getsortedzoomparcelsview, \
    getallzoomparcelsview, convertcoordinatesview

urlpatterns = [
    path('', homepageview, name='homepage'),
    path('searchparcelgeneral/<str:term>/<str:page_number>', searchparcelgeneral, name="searchparcelgeneral"),
    path('searchparcelbypoint/<str:easting_longitude>/<str:northing_latitude>/<str:srid>/<str:page_number>',
         searchparcelbypoint, name="searchparcelbypoint"),
    path('searchparcelbyfeaturetype/<str:feature>/<str:srid>/<str:page_number>', searchparcelbyfeaturetype,
         name="searchparcelbyfeaturetype"),
    path('parceldetail/<str:code>', parceldetailview, name="parceldetail"),
    path('parcelownerdetail/<str:code>', parcelownerdetailview, name="parcelownerdetail"),
    path('sortedzoomparcels/<str:longitude1>/<str:latitude1>/<str:longitude2>/<str:latitude2>/<str:number>',
         getsortedzoomparcelsview, name="sortedzoomparcels"),
    path('allzoomparcels/<str:longitude1>/<str:latitude1>/<str:longitude2>/<str:latitude2>',
         getallzoomparcelsview, name="allzoomparcels"),
    path('convertcoordinates/<str:oldsrid>/<str:oldfeature>/<str:newsrid>',
         convertcoordinatesview, name='convertcoordinates'),
]