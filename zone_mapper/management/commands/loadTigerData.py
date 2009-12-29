
# adpated from:
# ./manage.py ogrinspect ../../tiger_data/tl_2008_us_zcta5.shp zcta --mapping --multi
# and http://geodjango.org/docs/tutorial.html

from django.core.management.base import LabelCommand

import os
from zone_mapper.models import Zcta
from zone_mapper.surcharges import getDeliveryZips, getSurchargeZips
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.gdal.layer import Layer
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal.prototypes import ds as capi

class ZctaLayer(Layer):

    def __init__(self, layer_ptr, ds):
        super(ZctaLayer, self).__init__(layer_ptr, ds)
        self._deliveryZips = getDeliveryZips()
        self._numZips = len(self._deliveryZips)

        # walk through and establish a mapping between the index we
        # present to the client, and the index we use in the file
        self._indexMapping = []

        # adpted this logic from Layer.__getitem__
        for i in range(self.num_feat):
            ft = self._make_feature(i)
            if ft['ZCTA5CE'].as_int() in self._deliveryZips:
                self._indexMapping.append(i)

        if not len(self._indexMapping) == self._numZips:
            zips_not_found = []
            for z in self._deliveryZips:
                found = False
                for ft in self:
                    if ft['ZCTA5CE'].as_int() == z:
                        found = True
                        break
                if not found:
                    zips_not_found.append(str(z))
            except_text = 'Following zip codes were not found: ' 
            except_text += ', '.join(zips_not_found) + '. Aborting'
            raise Exception(except_text)

    def __getitem__(self, index):
        # adpting logic from Layer.__getitem__
        if isinstance(index, (int, long)):
            # accessing a single element
            if index < 0 or index >= self._numZips:
                raise OGRIndexError('Index requested out of range')
            item = self._make_feature(self._indexMapping[index])
            return item
        elif isinstance(index, slice):
            # slice requested
            result = []
            for clientId in xrange(index.indices(self._numZips)):
                item = self._make_feature(self._indexMapping(clientId))
                result.append(item)
            return result
        else:
            raise TypeError('Integers and slices may only be used when indexing OGR Layers.')

    def __iter__(self):
        # adpted from Layer.__iter__
        for i in xrange(self._numZips):
            rawft = capi.get_feature(self._ptr, self._indexMapping[i])
            yield Feature(rawft, self._ldefn)

    def __len__(self):
        return self._numZips


class ZctaSource(DataSource):

    def __getitem__(self, index):
        item = super(ZctaSource, self).__getitem__(index)
        betterItem = ZctaLayer(item.ptr, item._ds)
        return betterItem


class Command(LabelCommand):

    help = "Loads the given Tiger ZCTA SHP file into the db, and trims it down to minimal size."
    args = 'tigerPath'
    label = 'path to a Tiger ZCTA SHP file'

    zcta_mapping = {
        'zcta' : 'ZCTA5CE',
        #'classfp' : 'CLASSFP',     # not needed
        #'mtfcc' : 'MTFCC',         # not needed
        #'funcstat' : 'FUNCSTAT',   # not needed
        'geom' : 'MULTIPOLYGON',
    }


    def handle_label(self, tigerPath, **options):
        # first clear out any existing data from the db
        Zcta.objects.all().delete()

        tigerAbsPath = os.path.abspath(os.path.join(os.getcwd(), tigerPath))
        ds = ZctaSource(tigerAbsPath)

        lm = LayerMapping(Zcta, ds, Command.zcta_mapping)
        lm.save()

        # now go through the database and update eveyrone for the surcharges
        surchargZips = getSurchargeZips()
        zctas = Zcta.objects.all()
        for z in zctas:
            z.surcharge = z.zcta in surchargZips
            z.save()

