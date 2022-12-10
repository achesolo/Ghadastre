from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Country, CoordinateSystem, Region, District, Town, ParcelOwner, Parcel
from leaflet.admin import LeafletGeoAdmin


# Register your models here.

class CoordinateSystemResource(resources.ModelResource):
    class Meta:
        model = CoordinateSystem


class CoordinateSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'srid', 'unitname', 'created', 'updated')
    search_fields = ('name', 'code', 'srid', 'unitname', 'created', 'updated')

    # resource_classes = [CoordinateSystemResource]


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country


class CountryAdmin(LeafletGeoAdmin, ImportExportModelAdmin):
    list_display = ('name', 'code', 'notes', 'created', 'updated')
    search_fields = ('name', 'code', 'notes', 'created', 'updated')

    resource_classes = [CountryResource]


class RegionResource(resources.ModelResource):
    class Meta:
        model = Region


class RegionAdmin(LeafletGeoAdmin, ImportExportModelAdmin):
    list_display = ('name', 'code', 'notes', 'created', 'updated')
    search_fields = ('name', 'code', 'notes', 'created', 'updated')

    resource_classes = [RegionResource]


class DistrictResource(resources.ModelResource):
    class Meta:
        model = District


class DistrictAdmin(LeafletGeoAdmin):
    list_display = ('name', 'code', 'notes', 'created', 'updated')
    search_fields = ('name', 'code', 'notes', 'created', 'updated')

    # resource_classes = [DistrictResource]


class TownResource(resources.ModelResource):
    class Meta:
        model = Town


class TownAdmin(LeafletGeoAdmin):
    list_display = ('name', 'code', 'notes', 'created', 'updated')
    search_fields = ('name', 'code', 'notes', 'created', 'updated')

    # resource_classes = [TownResource]


class ParcelOwnerResource(resources.ModelResource):
    class Meta:
        model = ParcelOwner


class ParcelOwnerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'email', 'notes', 'created', 'updated')
    search_fields = ('code', 'firstname', 'surname', 'othernames', 'email', 'country',
                     'region', 'district', 'town', 'telephone1', 'telephone2',
                     'addressline1', 'addressline2', 'created', 'updated')

    # resource_classes = [ParcelOwnerResource]


class ParcelResource(resources.ModelResource):
    class Meta:
        model = Parcel


class ParcelAdmin(LeafletGeoAdmin):
    list_display = ('owner', 'code', 'parcelCRS', 'parcelboundaryDEFAULT', 'parcelboundaryWGS84',
                    'notes', 'created', 'updated')
    search_fields = ('code', 'created', 'updated')

    # resource_classes = [ParcelResource]


admin.site.register(CoordinateSystem, CoordinateSystemAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Town, DistrictAdmin)
admin.site.register(ParcelOwner, ParcelOwnerAdmin)
admin.site.register(Parcel, ParcelAdmin)
