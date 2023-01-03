from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.gis.geos import GEOSGeometry, Polygon
from .models import Parcel, ParcelOwner, CoordinateSystem
# from account.models import ParcelSetting

# Create your views here.


def searchparcelgeneral(request, term, page_number):
    number_of_pages = None
    parcels = None
    try:
        parcels = Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(code__icontains=term) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(town__name__icontains=term) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(owner__code__icontains=term) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(owner__firstname__icontains=term) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(owner__surname__icontains=term) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(owner__othernames__icontains=term)

        parcels = parcels.order_by('id')

        if parcels:
            paginator = Paginator(parcels, 10)
            number_of_pages = paginator.num_pages

            parcels = paginator.page(int(page_number))
            for parcel in parcels:
                parcel['parcelboundaryWGS84'] = parcel['parcelboundaryWGS84'].wkt
            parcels = list(parcels)

        else:
            parcels = None

    except Parcel.DoesNotExist:
        parcels = parcels

    results = {"parcels": parcels, "number_of_pages": number_of_pages}

    return JsonResponse(results, safe=False)


def searchparcelbypoint(request, easting_longitude, northing_latitude, srid, page_number):
    parcels = None
    number_of_pages = None
    try:
        point_wkt = f"POINT ({easting_longitude} {northing_latitude})"
        point_geom = GEOSGeometry(srid=int(srid), geo_input=point_wkt)
        point_geomWGS84 = point_geom.transform(4326, point_geom)

        parcels = Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__covers=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__overlaps=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__within=point_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__equals=point_geomWGS84)

        parcels = parcels.order_by('id')

        if parcels:
            paginator = Paginator(parcels, 10)
            number_of_pages = paginator.num_pages

            parcels = paginator.page(int(page_number))
            for parcel in parcels:
                parcel['parcelboundaryWGS84'] = parcel['parcelboundaryWGS84'].wkt
            parcels = list(parcels)

        else:
            parcels = None

    except:
        pass

    results = {"parcels": parcels, "number_of_pages": number_of_pages}

    return JsonResponse(results, safe=False)


def searchparcelbyfeaturetype(request, feature, srid, page_number):
    parcels = None
    number_of_pages = None
    try:
        feature = str(feature).replace("\n", "")
        feature_geom = GEOSGeometry(srid=int(srid), geo_input=feature)
        feature_geomWGS84 = feature_geom.transform(4326, feature_geom)

        parcels = Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__covers=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__overlaps=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__within=feature_geomWGS84) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84', 'owner__firstname', 'owner__surname',
                                        'owner__othernames').filter(parcelboundaryWGS84__equals=feature_geomWGS84)

        parcels = parcels.order_by('id')

        if parcels:
            paginator = Paginator(parcels, 10)
            number_of_pages = paginator.num_pages

            parcels = paginator.page(int(page_number))
            for parcel in parcels:
                parcel['parcelboundaryWGS84'] = parcel['parcelboundaryWGS84'].wkt
            parcels = list(parcels)

        else:
            parcels = None

    except:
        pass

    results = {"parcels": parcels, "number_of_pages": number_of_pages}

    return JsonResponse(results, safe=False)


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

    return render(request, "parcels/home.html", {'coordinatesystems': coordinatesystems})


def getsortedzoomparcelsview(request, longitude1, latitude1, longitude2, latitude2, number):
    # # The two coordinate pairs are the bounding box of the current screen zoom
    #
    parcels = None
    try:
        polygon = Polygon.from_bbox([longitude1, latitude1, longitude2, latitude2])
        polygon.srid = 4326

        parcels = Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
            parcelboundaryWGS84__covers=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__overlaps=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__within=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__equals=polygon)

        if parcels:
            parcels = parcels[: int(number)]
            for parcel in parcels:
                parcel['parcelboundaryWGS84'] = parcel['parcelboundaryWGS84'].wkt

        else:
            parcels = None

    except:
        pass

    return JsonResponse(parcels, safe=False)


def getallzoomparcelsview(request, longitude1, latitude1, longitude2, latitude2):
    # # The two coordinate pairs are the bounding box of the current screen zoom
    #
    parcels = None
    try:
        polygon = Polygon.from_bbox([longitude1, latitude1, longitude2, latitude2])
        polygon.srid = 4326

        parcels = Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
            parcelboundaryWGS84__covers=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__overlaps=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__within=polygon) | \
                  Parcel.objects.values('id', 'code', 'area', 'perimeter', 'parcelCRS__unitsymbol',
                                        'parcelboundaryWGS84').filter(
                      parcelboundaryWGS84__equals=polygon)

        if parcels:
            parcels = list(parcels)
            for parcel in parcels:
                parcel['parcelboundaryWGS84'] = parcel['parcelboundaryWGS84'].wkt

        else:
            parcels = None

    except:
        pass

    return JsonResponse(parcels, safe=False)


def convertcoordinatesview(request, oldsrid, oldfeature, newsrid):
    new_feature = None
    try:
        old_feature = str(oldfeature).replace("\n", "")
        old_feature_geom = GEOSGeometry(srid=int(oldsrid), geo_input=old_feature)

        new_feature = old_feature_geom.transform(int(newsrid), old_feature_geom)

        new_feature = [{"wkt": new_feature.wkt}, ]

    except:
        pass

    return JsonResponse(new_feature, safe=False)


