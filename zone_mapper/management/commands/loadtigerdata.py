
# adpated from:
# ./manage.py ogrinspect ../../tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi
# and http://geodjango.org/docs/tutorial.html

from os.path import abspath
from warnings import warn

from django.core.management.base import LabelCommand

from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.gdal.layer import Layer
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal.prototypes import ds as capi

from zone_mapper.models import Zone, ZipCode, Zcta

class ZctaLayer(Layer):

    def __init__(self, layer_ptr, ds):
        super(ZctaLayer, self).__init__(layer_ptr, ds)

        self._pknum = 0
        self._pkorder = list()
        self._pk2ftnum = dict()

        # adpted this logic from Layer.__getitem__
        for ftnum in range(self.num_feat):
            ft = super(ZctaLayer, self).__getitem__(ftnum)
            zipcode = ft['ZCTA5CE'].as_int()
            try:
                zipcode = ZipCode.objects.get(zipcode=zipcode)
            except ZipCode.DoesNotExist:
                continue
            self._pk2ftnum[zipcode.pk] = ftnum; 
            self._pkorder.append(zipcode.pk)

        self._pknum = len(self._pkorder)

        for zipcode in ZipCode.objects.all():
            if not self._pk2ftnum.has_key(zipcode.pk):
                warn("Zip Code %i in db but not in shape file, ignoring." %
                     zipcode.zipcode, RuntimeWarning)

    def __getitem__(self, index):
        # adpting logic from Layer.__getitem__
        if isinstance(index, (int, long)):
            try:
                pk = self._pkorder[index]
            except IndexError:
                raise OGRIndexError("Index requested out of range")
            fr = super(ZctaLayer, self).__getitem__(self._pk2ftnum(pk))
            return ft;

        if isinstance(index, slice):
            # slice requested
            result = []
            for clientId in xrange(index.indices(self._pknum)):
                result.append(self[clientId])
            return result

        raise TypeError("Only ints and slices can be used when " +
                        "indexing OGR Layers.")

    def __iter__(self):
        # adpted from Layer.__iter__
        for pk in self._pkorder:
            rawft = capi.get_feature(self._ptr, self._pk2ftnum[pk])
            yield Feature(rawft, self._ldefn)

    def __len__(self):
        return self._pknum


class ZctaSource(DataSource):

    def __getitem__(self, index):
        item = super(ZctaSource, self).__getitem__(index)
        betterItem = ZctaLayer(item.ptr, item._ds)
        return betterItem


class Command(LabelCommand):

    help = "Loads the needed data from given Tiger ZCTA SHP file into " +
           "the database"
    args = "tigerpath"
    label = "path to a Tiger ZCTA SHP file"

    zcta_mapping = {
        'zipcode' : {'zipcode': 'ZCTA5CE'},
        #'classfp' : 'CLASSFP',     # not needed
        #'mtfcc' : 'MTFCC',         # not needed
        #'funcstat' : 'FUNCSTAT',   # not needed
        'geom' : 'MULTIPOLYGON',
    }

    def handle_label(self, tigerpath, **options):

        ds = ZctaSource(abspath(tigerpath))
        lm = LayerMapping(Zcta, ds, Command.zcta_mapping)
        lm.save()

