"""
Zone Mapper database layer.

Adpated from:
./manage.py ogrinspect tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi
"""

from django.contrib.gis.db import models
from django.contrib.gis.geos.collections import MultiPolygon


class Zone(models.Model):
    "A set of ZipCodes with a particular color and border"
    objects = models.GeoManager()

    name = models.CharField(unique=True, max_length=31)
    fill_color = models.CharField(max_length=31)

    # if border_width is 0 or missing, it means no border.
    border_width = models.PositiveIntegerField(blank=True, default=0)
    border_color = models.CharField(blank=True, max_length=31)

    def __unicode__(self):
        return self.name

    def multipoly(self):
        """Get the multipolygon for this zone."""
        multipoly = None
        # exclude zipcodes for which there was nothing in the shp file
        zipcode_qs = self.zipcode_set.exclude(zcta__isnull=True)
        if zipcode_qs.count():
            zipcodes = zipcode_qs.all()
            multipoly = zipcodes[0].zcta.geom
            for zipcode in zipcodes[1:]:
                multipoly = multipoly.union(zipcode.zcta.geom)
                # the multipolygon.union() can return a straight polygon
            if not isinstance(multipoly, MultiPolygon):
                multipoly = MultiPolygon(multipoly)
        return multipoly

    def orphan_zipcodes(self):
        """Get the ZipCodes for this zone that have no shape info."""
        return self.zipcode_set.filter(zcta__isnull=True)


class ZipCode(models.Model):
    "ZipCodes that make up a Zone"

    class Meta:
        verbose_name = 'Zip Code'
        ordering = ['zipcode',]

    # TODO: min/max bounds?
    zipcode = models.IntegerField(unique=True, verbose_name='Zip Code')
    zone = models.ForeignKey(Zone)

    def __unicode__(self):
        return '%05i' % self.zipcode


class Zcta(models.Model):
    "Shape information for a ZipCode. Filled in from tiger data."
    objects = models.GeoManager()

    # TODO: min/max bounds?
    zipcode = models.OneToOneField(ZipCode, primary_key=True,
                                   db_column='zipcode', to_field='zipcode')

    #classfp = models.CharField(max_length=2)    # don't need
    #mtfcc = models.CharField(max_length=5)      # don't need
    #funcstat = models.CharField(max_length=1)   # don't need
    geom = models.MultiPolygonField()
