from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CoordinateSystem(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="UNIQUE CODE")
    srid = models.IntegerField(unique=True, verbose_name="SPATIAL REFERENCE ID / EPSG CODE")
    name = models.CharField(max_length=250, unique=True, verbose_name="NAME")
    unitname = models.CharField(max_length=250, verbose_name="UNIT NAME")
    unitsymbol = models.CharField(max_length=250, verbose_name="UNIT SYMBOL")
    notes = models.TextField(blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, null=True, verbose_name="FILES")
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "COORDINATE SYSTEM"
        verbose_name_plural = "COORDINATE SYSTEMS"


class Country(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="UNIQUE CODE")
    name = models.CharField(max_length=250, unique=True, verbose_name="NAME")
    countryboundaryCRS = models.ForeignKey(CoordinateSystem, related_name="coordinatesystem_countries",
                                     on_delete=models.CASCADE, verbose_name="BOUNDARY COORDINATE SYSTEM")
    countryboundaryDEFAULT = models.TextField(blank=True, null=True,
                                       verbose_name="BOUNDARY POLYGON DATA(<<{WKT}FORMAT>>)")
    countryboundaryWGS84 = models.PolygonField(blank=True, null=True, srid=4326,
                                              verbose_name="BOUNDARY MAP VIEW")  # WGS 84
    area = models.DecimalField(blank=True, null=True, verbose_name="AREA", max_digits=50, decimal_places=9)
    perimeter = models.DecimalField(blank=True, null=True, verbose_name="PERIMETER", max_digits=50, decimal_places=9)
    center = models.CharField(blank=True, null=True, verbose_name="CENTER", max_length=1000)
    notes = models.TextField(blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, null=True, verbose_name="FILES")
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")
    # validators=[validatecountrygeometryinput],

    def clean(self):
        if self.countryboundaryDEFAULT:
            self.countryboundaryDEFAULT = str(self.countryboundaryDEFAULT).replace("\n", "")
            try:
                geometry = GEOSGeometry(srid=self.countryboundaryCRS.srid,
                                        geo_input=self.countryboundaryDEFAULT)

            except:
                error = {'countryboundaryDEFAULT': _("Incorrect format!. Format must be WKT or GEOJSON")}
                raise ValidationError(error)

            if geometry.hasz:
                error = {'countryboundaryDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not geometry.empty:
                if str(geometry.geom_type) != "Polygon":
                    error = {'countryboundaryDEFAULT': _("Only polygon geometry is accepted!")}
                    raise ValidationError(error)

                else:
                    geometryWGS84 = geometry.transform(4326, geometry)
                    # Checking if the region geometry does not overlap with or
                    # is covers any other region geometry.
                    conflicting_countries = Country.objects.filter(countryboundaryWGS84__covers=geometryWGS84) | \
                                          Country.objects.filter(countryboundaryWGS84__overlaps=geometryWGS84) | \
                                          Country.objects.filter(countryboundaryWGS84__within=geometryWGS84) | \
                                          Country.objects.filter(countryboundaryWGS84__equals=geometryWGS84)

                    conflicting_countries = list(conflicting_countries)
                    if self in conflicting_countries:
                        conflicting_countries.remove(self)

                    if conflicting_countries:
                        conflicting_countries_str = ""
                        for country in conflicting_countries:
                            conflicting_countries_str += "{" + country.code + ">>" + country.name + "}, "

                        error = {'countryboundaryDEFAULT': _("Country boundary conflicts with the boundary of << "
                                                     ""+ conflicting_countries_str + " >>")}
                        raise ValidationError(error)

            else:
                error = {'countryboundaryDEFAULT': _("Does not accept empty geometry!")}
                raise ValidationError(error)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.countryboundaryDEFAULT:
            self.countryboundaryDEFAULT = str(self.countryboundaryDEFAULT).replace("\n", "")

            countryboundaryDEFAULTGEOMETRY = GEOSGeometry(srid=self.countryboundaryCRS.srid,
                                           geo_input=self.countryboundaryDEFAULT)
            self.countryboundaryDEFAULT = countryboundaryDEFAULT.wkt

            self.countryboundaryWGS84 = countryboundaryDEFAULTGEOMETRY.transform(
                4326, countryboundaryDEFAULTGEOMETRY)

            self.area = countryboundaryDEFAULTGEOMETRY.area
            self.perimeter = countryboundaryDEFAULTGEOMETRY.length
            self.center = str(countryboundaryDEFAULTGEOMETRY.centroid.coords)

            super(Country, self).save(*args, **kwargs)

        else:
            self.countryboundaryWGS84 = None
            self.area = None
            self.perimeter = None
            self.center = None
            super(Country, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "COUNTRY"
        verbose_name_plural = "COUNTRIES"


class Region(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="UNIQUE CODE")
    name = models.CharField(max_length=250, unique=True, verbose_name="NAME")
    country = models.ForeignKey(Country, related_name="country_regions",
                                on_delete=models.CASCADE, verbose_name="COUNTRY")
    regionboundaryCRS = models.ForeignKey(CoordinateSystem, related_name="coordinatesystem_regions",
                                           on_delete=models.CASCADE, verbose_name="BOUNDARY COORDINATE SYSTEM")
    regionboundaryDEFAULT = models.TextField(blank=True, null=True,
                                      verbose_name="BOUNDARY POLYGON DATA(<<{WKT}FORMAT>>)")
    regionboundaryWGS84 = models.PolygonField(blank=True, null=True, srid=4326,
                                             verbose_name="BOUNDARY MAP VIEW")  # WGS 84
    area = models.DecimalField(blank=True, null=True, verbose_name="AREA", max_digits=50, decimal_places=9)
    perimeter = models.DecimalField(blank=True, null=True, verbose_name="PERIMETER", max_digits=50, decimal_places=9)
    center = models.CharField(blank=True, null=True, verbose_name="CENTER", max_length=1000)
    notes = models.TextField(blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, null=True, verbose_name="FILES")
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED ON")

    def clean(self):
        if self.regionboundaryDEFAULT:
            self.regionboundaryDEFAULT = str(self.regionboundaryDEFAULT).replace("\n", "")

            try:
                geometry = GEOSGeometry(srid=self.regionboundaryCRS.srid,
                                        geo_input=self.regionboundaryDEFAULT)

            except:
                error = {'regionboundaryDEFAULT': _("Incorrect format!. Format must be WKT or GEOJSON")}
                raise ValidationError(error)

            if geometry.hasz:
                error = {'regionboundaryDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not geometry.empty:
                if str(geometry.geom_type) != "Polygon":
                    error = {'regionboundaryDEFAULT': _("Only polygon geometry is accepted!")}
                    raise ValidationError(error)

                else:
                    geometryWGS84 = geometry.transform(4326, geometry)
                    if self.country.countryboundaryWGS84:
                        # Checking if the region geometry is within the country geometry
                        if not self.country.countryboundaryWGS84.covers(geometryWGS84):
                            error = {'regionboundaryDEFAULT': _("Region boundary is not within the boundary "
                                                         "of the selected Country!")}
                            raise ValidationError(error)

                        else:
                            # Checking if the region geometry does not overlap with or
                            # is covers any other region geometry.
                            conflicting_regions = Region.objects.filter(
                                country=self.country, regionboundaryWGS84__covers=geometryWGS84) | \
                                Region.objects.filter(country=self.country,
                                                      regionboundaryWGS84__overlaps=geometryWGS84) | \
                                Region.objects.filter(country=self.country,
                                                      regionboundaryWGS84__within=geometryWGS84) | \
                                Region.objects.filter(country=self.country,
                                                      regionboundaryWGS84__equals=geometryWGS84)

                            conflicting_regions = list(conflicting_regions)
                            if self in conflicting_regions:
                                conflicting_regions.remove(self)

                            if conflicting_regions:
                                conflicting_regions_str = ""
                                for region in conflicting_regions:
                                    conflicting_regions_str += "{" + region.code + ">>" + region.name + "}, "

                                error = {'regionboundaryDEFAULT': _("Region boundary conflicts with boundary << "
                                                             ""+ conflicting_regions_str + " >>")}
                                raise ValidationError(error)

                    else:
                        error = {'regionboundaryDEFAULT': _("Clear Field! Region cannot have any boundary "
                                                     "since Country has no boundary.")}
                        raise ValidationError(error)

            else:
                error = {'regionboundaryDEFAULT': _("Does not accept empty geometry!")}
                raise ValidationError(error)

    def __str__(self):
        return f"{self.country.name} >> {self.name}"

    def save(self, *args, **kwargs):
        if self.regionboundaryDEFAULT:
            self.regionboundaryDEFAULT = str(self.regionboundaryDEFAULT).replace("\n", "")

            regionboundaryDEFAULTGEOMETRY = GEOSGeometry(srid=self.regionboundaryCRS.srid,
                                                          geo_input=self.regionboundaryDEFAULT)
            self.regionboundaryDEFAULT = regionboundaryDEFAULT.wkt

            self.regionboundaryWGS84 = regionboundaryDEFAULTGEOMETRY.transform(
                4326, regionboundaryDEFAULTGEOMETRY)

            self.area = regionboundaryDEFAULTGEOMETRY.area
            self.perimeter = regionboundaryDEFAULTGEOMETRY.length
            self.center = str(regionboundaryDEFAULTGEOMETRY.centroid.coords)

            super(Region, self).save(*args, **kwargs)

        else:
            self.regionpolygonWGS84 = None
            self.area = None
            self.perimeter = None
            self.center = None
            super(Region, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "REGION"
        verbose_name_plural = "REGIONS"


class District(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250, unique=True)
    region = models.ForeignKey(Region, related_name="region_districts",
                               on_delete=models.CASCADE)
    districtboundaryCRS = models.ForeignKey(CoordinateSystem, related_name="coordinatesystem_districts",
                                     on_delete=models.CASCADE, verbose_name="BOUNDARY COORDINATE SYSTEM")
    districtboundaryDEFAULT = models.TextField(blank=True, null=True,
                                      verbose_name="BOUNDARY POLYGON DATA(<<{WKT}FORMAT>>)")
    districtboundaryWGS84 = models.PolygonField(blank=True, null=True, srid=4326,
                                             verbose_name="BOUNDARY MAP VIEW")  # WGS 84
    area = models.DecimalField(blank=True, null=True, verbose_name="AREA", max_digits=50, decimal_places=9)
    perimeter = models.DecimalField(blank=True, null=True, verbose_name="PERIMETER", max_digits=50, decimal_places=9)
    center = models.CharField(blank=True, null=True, verbose_name="CENTER", max_length=1000)
    notes = models.TextField(max_length=1000000, blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, verbose_name="FILES")  # Will fill tho
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")

    def clean(self):
        if self.districtboundaryDEFAULT:
            self.districtboundaryDEFAULT = str(self.districtboundaryDEFAULT).replace("\n", "")

            try:
                geometry = GEOSGeometry(srid=self.districtboundaryCRS.srid,
                                        geo_input=self.districtboundaryDEFAULT)

            except:
                error = {'districtboundaryDEFAULT': _("Incorrect format!. Format must be WKT or GEOJSON")}
                raise ValidationError(error)

            if geometry.hasz:
                error = {'districtboundaryDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not geometry.empty:
                if str(geometry.geom_type) != "Polygon":
                    error = {'districtboundaryDEFAULT': _("Only polygon geometry is accepted!")}
                    raise ValidationError(error)

                else:
                    geometryWGS84 = geometry.transform(4326, geometry)
                    if self.region.regionboundaryWGS84:
                        # Checking if the district geometry is within the region geometry
                        if not self.region.regionboundaryWGS84.covers(geometryWGS84):
                            error = {'districtboundaryDEFAULT': _("District boundary is not within the boundary "
                                                         "of the selected Region!")}
                            raise ValidationError(error)

                        else:
                            # Checking if the region geometry does not overlap with or
                            # is covers any other region geometry.
                            conflicting_districts = District.objects.filter(
                                region=self.region, districtboundaryWGS84__covers=geometryWGS84) | \
                                                  District.objects.filter(region=self.region,
                                                                        districtboundaryWGS84__overlaps=geometryWGS84) | \
                                                  District.objects.filter(region=self.region,
                                                                        districtboundaryWGS84__within=geometryWGS84) | \
                                                  District.objects.filter(region=self.region,
                                                                        districtboundaryWGS84__equals=geometryWGS84)

                            conflicting_districts = list(conflicting_districts)
                            if self in conflicting_districts:
                                conflicting_districts.remove(self)

                            if conflicting_districts:
                                conflicting_districts_str = ""
                                for district in conflicting_districts:
                                    conflicting_districts_str += "{" + district.code + ">>" + district.name + "}, "

                                error = {'districtboundaryDEFAULT': _("District boundary conflicts with boundary << "
                                                             ""+ conflicting_regions_str + " >>")}
                                raise ValidationError(error)

                    else:
                        error = {'districtboundaryDEFAULT': _("Clear Field! District cannot have any boundary "
                                                     "since Region has no boundary.")}
                        raise ValidationError(error)

            else:
                error = {'districtboundaryDEFAULT': _("Does not accept empty geometry!")}
                raise ValidationError(error)

    def __str__(self):
        return f"{self.region.country.name} >> {self.region.name} >> {self.name}"

    def save(self, *args, **kwargs):
        if self.districtboundaryDEFAULT:
            self.districtboundaryDEFAULT = str(self.districtboundaryDEFAULT).replace("\n", "")

            districtboundaryDEFAULTGEOMETRY = GEOSGeometry(srid=self.districtboundaryCRS.srid,
                                                          geo_input=self.districtboundaryDEFAULT)
            self.districtboundaryDEFAULT = districtboundaryDEFAULT.wkt

            self.districtboundaryWGS84 = countryboundaryDEFAULTGEOMETRY.transform(
                4326, districtboundaryDEFAULTGEOMETRY)

            self.area = districtboundaryDEFAULTGEOMETRY.area
            self.perimeter = districtboundaryDEFAULTGEOMETRY.length
            self.center = str(districtboundaryDEFAULTGEOMETRY.centroid.coords)

            super(District, self).save(*args, **kwargs)

        else:
            self.districtpolygonWGS84 = None
            self.area = None
            self.perimeter = None
            self.center = None
            super(District, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "DISTRICT"
        verbose_name_plural = "DISTRICTS"


class Town(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250, unique=True)
    district = models.ForeignKey(District, related_name="district_towns",
                                 on_delete=models.CASCADE)
    townboundaryCRS = models.ForeignKey(CoordinateSystem, related_name="coordinatesystem_towns",
                                    on_delete=models.CASCADE, verbose_name="BOUNDARY COORDINATE SYSTEM")
    townboundaryDEFAULT = models.TextField(blank=True, null=True,
                                        verbose_name="BOUNDARY POLYGON DATA(<<{WKT}FORMAT>>)")
    townboundaryWGS84 = models.PolygonField(blank=True, null=True, srid=4326,
                                               verbose_name="BOUNDARY MAP VIEW")  # WGS 84
    area = models.DecimalField(blank=True, null=True, verbose_name="AREA", max_digits=50, decimal_places=9)
    perimeter = models.DecimalField(blank=True, null=True, verbose_name="PERIMETER", max_digits=50, decimal_places=9)
    center = models.CharField(blank=True, null=True, verbose_name="CENTER", max_length=1000)
    notes = models.TextField(max_length=1000000, blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, verbose_name="FILES")  # Will fill tho
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")

    def clean(self):
        if self.townboundaryDEFAULT:
            self.townboundaryDEFAULT = str(self.townboundaryDEFAULT).replace("\n", "")

            try:
                geometry = GEOSGeometry(srid=self.townboundaryCRS.srid,
                                        geo_input=self.townboundaryDEFAULT)

            except:
                error = {'townboundaryDEFAULT': _("Incorrect format!. Format must be WKT or GEOJSON")}
                raise ValidationError(error)

            if geometry.hasz:
                error = {'townboundaryDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not geometry.empty:
                if str(geometry.geom_type) != "Polygon":
                    error = {'townboundaryDEFAULT': _("Only polygon geometry is accepted!")}
                    raise ValidationError(error)

                else:
                    geometryWGS84 = geometry.transform(4326, geometry)
                    if self.district.districtboundaryWGS84:
                        # Checking if the town geometry is within the district geometry
                        if not self.district.districtboundaryWGS84.covers(geometryWGS84):
                            error = {'townboundaryDEFAULT': _("Town boundary is not within the boundary "
                                                           "of the selected District!")}
                            raise ValidationError(error)

                        else:
                            # Checking if the region geometry does not overlap with or
                            # is covers any other region geometry.
                            conflicting_towns = Town.objects.filter(
                                district=self.district, townboundaryWGS84__covers=geometryWGS84) | \
                                                    Town.objects.filter(district=self.district,
                                                                            townboundaryWGS84__overlaps=geometryWGS84) | \
                                                    Town.objects.filter(district=self.district,
                                                                            townboundaryWGS84__within=geometryWGS84) | \
                                                    Town.objects.filter(district=self.district,
                                                                            townboundaryWGS84__equals=geometryWGS84)

                            conflicting_towns = list(conflicting_towns)
                            if self in conflicting_towns:
                                conflicting_towns.remove(self)

                            if conflicting_towns:
                                conflicting_towns_str = ""
                                for town in conflicting_towns:
                                    conflicting_towns_str += "{" + town.code + ">>" + town.name + "}, "

                                error = {'townboundaryDEFAULT': _("Town boundary conflicts with boundary << "
                                                               ""+ conflicting_towns_str + " >>")}
                                raise ValidationError(error)

                    else:
                        error = {'townboundaryDEFAULT': _("Clear Field! Town cannot have any boundary "
                                                       "since District has no boundary.")}
                        raise ValidationError(error)

            else:
                error = {'townboundaryDEFAULT': _("Does not accept empty geometry!")}
                raise ValidationError(error)

    def __str__(self):
        return f"{self.district.region.country.name} >> {self.district.region.name} >> \
                 {self.district.name} >> {self.name}"

    def save(self, *args, **kwargs):
        if self.townboundaryDEFAULT:
            self.townboundaryDEFAULT = str(self.townboundaryDEFAULT).replace("\n", "")

            townboundaryDEFAULTGEOMETRY = GEOSGeometry(srid=self.townboundaryCRS.srid,
                                                           geo_input=self.townboundaryDEFAULT)
            self.townboundaryDEFAULT = townboundaryDEFAULT.wkt

            self.townboundaryWGS84 = townboundaryDEFAULTGEOMETRY.transform(
                4326, townboundaryDEFAULTGEOMETRY)

            self.area = townboundaryDEFAULTGEOMETRY.area
            self.perimeter = townboundaryDEFAULTGEOMETRY.length
            self.center = str(townboundaryDEFAULTGEOMETRY.centroid.coords)

            super(Town, self).save(*args, **kwargs)

        else:
            self.townpolygon = None
            self.townpolygonWGS84 = None
            self.area = None
            self.perimeter = None
            self.center = None
            super(Town, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "TOWN"
        verbose_name_plural = "TOWNS"


class ParcelOwner(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="UNIQUE CODE")
    firstname = models.CharField(max_length=50, blank=True, verbose_name="FIRST NAME")
    surname = models.CharField(max_length=50, blank=True, verbose_name="SURNAME")
    othernames = models.CharField(max_length=150, blank=True, verbose_name="OTHER NAMES")
    country = models.CharField(max_length=150, blank=True, verbose_name="NATIONALITY")
    region = models.CharField(max_length=150, blank=True, verbose_name="REGION")
    district = models.CharField(max_length=150, blank=True, verbose_name="DISTRICT")
    town = models.CharField(max_length=150, blank=True, verbose_name="TOWN")
    addressline1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="ADDRESS LINE 1")
    addressline2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="ADDRESS LINE 2")
    email = models.EmailField(blank=True, null=True, verbose_name="EMAIL")
    telephone1 = models.CharField(max_length=15, blank=True, null=True, verbose_name="TELEPHONE LINE 1")
    telephone2 = models.CharField(max_length=15, blank=True, null=True, verbose_name="TELEPHONE LINE 2")
    notes = models.TextField(max_length=1000000, blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, verbose_name="FILES")  # Will fill tho
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")

    def __str__(self):
        return f"{self.code} >> {self.firstname} {self.surname} {self.othernames}"

    class Meta:
        verbose_name = "PARCEL OWNER"
        verbose_name_plural = "PARCEL OWNERS"


class Parcel(models.Model):
    code = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(ParcelOwner, related_name="owner_parcels",
                              on_delete=models.CASCADE, blank=False)
    town = models.ForeignKey(Town, related_name="town_parcels", on_delete=models.CASCADE)
    parcelCRS = models.ForeignKey(CoordinateSystem, related_name="coordinatesystem_parcels",
                                     on_delete=models.CASCADE)
    parcelboundaryDEFAULT = models.TextField(blank=False,
                                    verbose_name="BOUNDARY POLYGON DATA(<<{WKT}FORMAT>>)")
    parcelreferenceDEFAULT = models.TextField(blank=True, null=True,
                                      verbose_name="REFERENCES MULTIPOINT DATA(<<{WKT}FORMAT>>)")
    parcelboundaryWGS84 = models.PolygonField(blank=True, null=True, srid=4326, editable=False,
                                             verbose_name="PARCEL POLYGON WGS84")  # WGS 84
    parcelreferenceWGS84 = models.MultiPointField(blank=True, null=True, srid=4326, editable=False,
                                         verbose_name="PARCEL REFERENCE POINT WGS84")  # WGS 84
    parcelgeometry = models.GeometryCollectionField(blank=True, null=True, srid=4326,
                                         verbose_name="PARCEL GEOMETRY MAP VIEW")  # WGS 84
    area = models.DecimalField(blank=True, null=True, verbose_name="AREA", max_digits=50, decimal_places=9)
    perimeter = models.DecimalField(blank=True, null=True, verbose_name="PERIMETER", max_digits=50, decimal_places=9)
    center = models.CharField(blank=True, null=True, verbose_name="CENTER", max_length=1000)
    notes = models.TextField(max_length=1000000, blank=True, verbose_name="NOTES")
    files = models.FileField(upload_to="documents", blank=True, verbose_name="FILES")  # Will fill tho
    registered = models.DateTimeField(blank=True, null=True, verbose_name="DATETIME REGISTERED")
    created = models.DateTimeField(auto_now_add=True, verbose_name="DATETIME CREATED")
    updated = models.DateTimeField(auto_now=True, verbose_name="DATETIME UPDATED")

    def clean(self):
        if self.parcelboundaryDEFAULT:
            self.parcelboundaryDEFAULT = str(self.parcelboundaryDEFAULT).replace("\n", "")

            try:
                boundary_geometry = GEOSGeometry(srid=self.parcelCRS.srid,
                                                 geo_input=self.parcelboundaryDEFAULT)

            except:
                error = {'parcelboundaryDEFAULT': _("Incorrect format!. Format must be WKT")}
                raise ValidationError(error)

            if boundary_geometry.hasz:
                error = {'parcelboundaryDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not boundary_geometry.empty:
                if str(boundary_geometry.geom_type) != "Polygon":
                    error = {'parcelboundaryDEFAULT': _("Only polygon geometry is accepted!")}
                    raise ValidationError(error)

                else:
                    boundary_geometryWGS84 = boundary_geometry.transform(4326, boundary_geometry)
                    if self.town.townboundaryWGS84:
                        # Checking if the town geometry is within the district geometry
                        if not self.town.townboundaryWGS84.covers(boundary_geometryWGS84):
                            error = {'parcelboundaryDEFAULT': _("Parcel boundary is not within the boundary "
                                                       "of the selected Town!")}
                            raise ValidationError(error)


                    # Checking if the region geometry does not overlap with or
                    # is covers any other region geometry.
                    conflicting_parcels = Parcel.objects.filter(
                        town=self.town, parcelboundaryWGS84__covers=boundary_geometryWGS84) | \
                        Parcel.objects.filter(
                            town=self.town, parcelboundaryWGS84__overlaps=boundary_geometryWGS84) | \
                        Parcel.objects.filter(
                            town=self.town, parcelboundaryWGS84__within=boundary_geometryWGS84) | \
                        Parcel.objects.filter(
                            town=self.town, parcelboundaryWGS84__equals=boundary_geometryWGS84)

                    conflicting_parcels = list(conflicting_parcels)
                    if self in conflicting_parcels:
                        conflicting_parcels.remove(self)

                    if conflicting_parcels:
                        conflicting_towns_str = ""
                        for parcel in conflicting_parcels:
                            conflicting_towns_str += "{" + parcel.code + " >>" + parcel.owner.firstname + \
                                    " " +  parcel.owner.surname + " " + parcel.owner.othernames + "}, "

                            error = {'parcelboundaryDEFAULT': _("Parcel boundary conflicts with the boundary of "
                                                             "Parcel << " + conflicting_towns_str + " >>")}
                            raise ValidationError(error)

            else:
                error = {'parcelboundaryDEFAULT': _("Does not accept empty geometry!")}
                raise ValidationError(error)

        # Validating the parcel reference
        if self.parcelreferenceDEFAULT:
            self.parcelreferenceDEFAULT = str(self.parcelreferenceDEFAULT).replace("\n", "")

            try:
                reference_geometry = GEOSGeometry(srid=self.parcelCRS.srid,
                                                 geo_input=self.parcelreferenceDEFAULT)

            except:
                error = {'parcelreferenceDEFAULT': _("Incorrect format!. Format must be WKT or GEOJSON")}
                raise ValidationError(error)

            if reference_geometry.hasz:
                error = {'parcelreferenceDEFAULT': _("Only two-dimension coordinate pairs are accepted!")}
                raise ValidationError(error)

            if not reference_geometry.empty:
                if str(reference_geometry.geom_type) != "MultiPoint":
                    error = {'parcelreferenceDEFAULT': _("Only multipoint geometry is accepted!")}
                    raise ValidationError(error)

    def __str__(self):
        return f"{self.code} >> {self.owner}"

    def save(self, *args, **kwargs):
        # GEOMETRYCOLLECTION ( POINT(2 3), LINESTRING(2 3, 3 4))

        if self.parcelboundaryDEFAULT:
            self.parcelboundaryDEFAULT = str(self.parcelboundaryDEFAULT).replace("\n", "")

            parcelboundaryDEFAULTGEOMETRY = GEOSGeometry(srid=self.parcelCRS.srid,
                                                       geo_input=self.parcelboundaryDEFAULT)
            self.parcelboundaryDEFAULT = parcelboundaryDEFAULTGEOMETRY.wkt
            self.parcelboundaryWGS84 = parcelboundaryDEFAULTGEOMETRY.transform(
                4326, parcelboundaryDEFAULTGEOMETRY)

            if self.parcelreferenceDEFAULT:
                self.parcelreferenceDEFAULT = str(self.parcelreferenceDEFAULT).replace("\n", "")

                parcelreferenceDEFAULTGEOMETRY = GEOSGeometry(srid=self.parcelCRS.srid,
                                                             geo_input=self.parcelreferenceDEFAULT)
                self.parcelreferenceDEFAULT = parcelreferenceDEFAULTGEOMETRY.wkt
                self.parcelreferenceWGS84 = parcelreferenceDEFAULTGEOMETRY.transform(
                    4326, parcelreferenceDEFAULTGEOMETRY)

                self.parcelgeometry = "GEOMETRYCOLLECTION (" + self.parcelboundaryWGS84.wkt + ", " + \
                                      self.parcelreferenceWGS84.wkt + ")"

            else:
                self.parcelgeometry = "GEOMETRYCOLLECTION (" + self.parcelboundaryWGS84.wkt + ")"

            self.area = parcelboundaryDEFAULTGEOMETRY.area
            self.perimeter = parcelboundaryDEFAULTGEOMETRY.length
            self.center = str(parcelboundaryDEFAULTGEOMETRY.centroid.coords)

            super(Parcel, self).save(*args, **kwargs)

        else:
            super(Parcel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "PARCEL"
        verbose_name_plural = "PARCELS"




