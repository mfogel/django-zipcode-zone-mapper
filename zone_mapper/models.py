
# adpated from:
# ./manage.py ogrinspect ../../tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi

# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models

class Zcta(models.Model):
    # Note: "LayerMapError: Django field type "PositiveIntegerField" has no OGR mapping (yet)." (08/24/09)
    zcta = models.IntegerField(primary_key=True) 
    surcharge = models.BooleanField(default=False)
    #classfp = models.CharField(max_length=2)    # don't need
    #mtfcc = models.CharField(max_length=5)      # don't need
    #funcstat = models.CharField(max_length=1)   # don't need

    # 900913 is the 'google SRID' (meaning mercator)
    # http://geodjango.org/docs/install.html#addgoogleprojection
    geom = models.MultiPolygonField(srid=900913)
    objects = models.GeoManager()

    def __str__(self):
        return 'Zip: %s' % self.zcta
