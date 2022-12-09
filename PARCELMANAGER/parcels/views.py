from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.geos import GEOSGeometry
from .models import Parcel, ParcelOwner, CoordinateSystem

# Create your views here.


def searchparcelgeneral(request, term):
    parcels = None
    try:
        parcels = Parcel.objects.values('id', 'code').filter(code__icontains=term) | \
                  Parcel.objects.values('id', 'code').filter(town__name__icontains=term) | \
                  Parcel.objects.values('id', 'code').filter(owner__code__icontains=term)

        if parcels:
            parcels = list(parcels)

        else:
            parcels = None

    except Parcel.DoesNotExist:
        parcels = parcels

    return JsonResponse(parcels, safe=False)


def searchparcelbypoint(request, easting_longitude, northing_latitude, srid):
    parcels = None
    try:
        point_wkt = f"POINT ({easting_longitude} {northing_latitude})"
        point_geom = GEOSGeometry(srid=int(srid), geo_input=point_wkt)
        point_geomWGS84 = point_geom.transform(4326, point_geom)

        parcels = Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__covers=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__overlaps=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__within=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__equals=point_geomWGS84)

        if parcels:
            parcels = list(parcels)

        else:
            parcels = None

    except:
        pass

    return JsonResponse(parcels, safe=False)


def searchparcelbyfeaturetype(request, feature, srid):
    parcels = None
    try:
        feature = str(feature).replace("\n", "")
        feature_geom = GEOSGeometry(srid=int(srid), geo_input=feature)
        feature_geomWGS84 = feature_geom.transform(4326, feature_geom)

        parcels = Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__covers=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__overlaps=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__within=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code').filter(parcelboundaryWGS84__equals=feature_geomWGS84)

        if parcels:
            parcels = list(parcels)

        else:
            parcels = None

    except:
        pass

    return JsonResponse(parcels, safe=False)


def parceldetailview(request, code):
    parcel = None
    try:
        parcel = Parcel.objects.get(code=code)

    except Parcel.DoesNotExist:
        parcel = parcel

    return render(request, "parcels/parcel_detail.html", {'parcel': parcel})


def parcelownerdetailview(request, code):
    parcelowner = None
    try:
        parcelowner = ParcelOwner.objects.get(code=code)

    except ParcelOwner.DoesNotExist:
        parcelowner = parcelowner

    return render(request, "parcels/parcelowner_detail.html", {"parcelowner": parcelowner})


def homepageview(request):

    coordinatesystems = CoordinateSystem.objects.all()
    parcels = Parcel.objects.all()

    return render(request, "parcels/home.html", {
        'parcels': parcels, 'coordinatesystems': coordinatesystems})

