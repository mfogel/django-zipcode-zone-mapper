
# adpated from:
# ./manage.py ogrinspect ../../tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi
# and http://geodjango.org/docs/tutorial.html

from os.path import abspath

from django.core.management.base import LabelCommand

from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.gdal.layer import Layer
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal.prototypes import ds as capi

from zone_mapper.models import Zone, ZipCode, Zcta

class Command(LabelCommand):

    help = ("Loads the needed data from given Tiger ZCTA SHP file into "
            "the database")
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

        datasource = ZctaSource(abspath(tigerpath))
        lm = LayerMapping(Zcta, datasource, Command.zcta_mapping)

        # warn about possible mispelled zipcodes
        if options.get('verbosity', 1):
            for layer in datasource:
                for zipcode in layer.get_missed_zipcodes():
                    print(("Warning: Zip Code %i in db but not in shape "
                           "file, ignoring.") % zipcode.zipcode)

        lm.save()


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

    def get_missed_zipcodes(self):
        missed = []
        for zipcode in ZipCode.objects.all():
            if not self._pk2ftnum.has_key(zipcode.pk):
                missed.append(zipcode)
        return missed

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

    def __init__(self, *args, **kwargs):
        super(ZctaSource, self).__init__(*args, **kwargs)
        self._data_sources = {}

    def __getitem__(self, index):
        if not self._data_sources.has_key(index):
            item = super(ZctaSource, self).__getitem__(index)
            self._data_sources[index] = ZctaLayer(item.ptr, item._ds)
        return self._data_sources[index]

