
# adpated from:
# ./manage.py ogrinspect tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi

from django.contrib.gis.db import models

# 900913 is the 'google SRID' (meaning mercator)
SRID = 900913

class Zone(models.Model):
    objects = models.GeoManager()

    name = models.CharField(unique=True, max_length=31)
    fill_color = models.CharField(max_length=31)

    # if border_width is 0 or missing, it means no border.
    border_width = models.PositiveIntegerField(blank=True, default=0)
    border_color = models.CharField(blank=True, max_length=31)

    geom = models.MultiPolygonField(srid=SRID, blank=True, editable=False,
                                    null=True, spatial_index=False)

    def __unicode__(self):
        return self.name

class ZipCode(models.Model):

    class Meta:
        verbose_name = 'Zip Code'

    id = models.AutoField(primary_key=True)
    # FIXME: min/max bounds?
    zipcode = models.IntegerField(unique=True, verbose_name='Zip Code')
    zone = models.ForeignKey(Zone)

    def __unicode__(self):
        return '%05i' % self.zipcode

class Zcta(models.Model):
    objects = models.GeoManager()

    # FIXME: min/max bounds?
    zipcode = models.OneToOneField(ZipCode, primary_key=True,
                                   db_column='zipcode', to_field='zipcode')

    #classfp = models.CharField(max_length=2)    # don't need
    #mtfcc = models.CharField(max_length=5)      # don't need
    #funcstat = models.CharField(max_length=1)   # don't need
    geom = models.MultiPolygonField(srid=SRID)


