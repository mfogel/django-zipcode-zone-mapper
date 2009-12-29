
from django.core.management.base import NoArgsCommand

from sys import stdout
from zone_mapper.models import Zcta

class Command(NoArgsCommand):

    help = "Builds the KML file for the current contents of the deliveryMap zcta database.  Output to stdout."

    def handle_noargs(self, **options):

        # collect all our polygons and merge them all together
        freeZctas = Zcta.objects.filter(surcharge=False)
        freeMultiPoly = None
        for fz in freeZctas:
            if freeMultiPoly is None: freeMultiPoly = fz.geom
            else: freeMultiPoly = freeMultiPoly.union(fz.geom)

        surchargeZctas = Zcta.objects.filter(surcharge=True)
        surchargeMultiPoly = None
        for sz in surchargeZctas:
            if surchargeMultiPoly is None: surchargeMultiPoly = sz.geom
            else: surchargeMultiPoly = surchargeMultiPoly.union(sz.geom)

        # now fill up a buffer list for the kml
        self.initKml()

        cnt = 0
        for p in freeMultiPoly:
            self.initPoly('transGreenPoly', cnt)
            self.addPoly(p)
            self.closePoly()
            cnt += 1

        cnt = 0
        for p in surchargeMultiPoly:
            self.initPoly('transYellowPoly', cnt)
            self.addPoly(p)
            self.closePoly()
            cnt += 1

        self.closeKml()
        self.printKml(verbose=True)

    def printKml(self, verbose=False):
        curIdent = 0
        for line in self._kmls:
            if line[0:2] == '</': curIdent -= 1
            if verbose: stdout.write('\t' * curIdent)
            stdout.write(line + '\n')
            if line[0] is '<' and line[1] is not '?':
                # this takes into account <tag>value</tag> lines
                if line.rfind('<') is not line.rfind('</'): 
                    curIdent += 1

    def initKml(self):
        self._kmls = []
        self._kmls.append('<?xml version="1.0" encoding="UTF-8"?>')
        self._kmls.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        self._kmls.append('<Document>')
        self.addStyle('transGreenPoly', '7d00ff00', 'd022ff22')
        self.addStyle('transYellowPoly', '7d00ffff', 'd022ffff')

    def addStyle(self, name, fillColor, lineColor):
        self._kmls.append('<Style id="%s">' % (name))
        self._kmls.append('<LineStyle>')
        self.addProperty('width', '3')
        self.addProperty('color', lineColor)
        self._kmls.append('</LineStyle>')
        self._kmls.append('<PolyStyle>')
        self.addProperty('color', fillColor)
        self._kmls.append('</PolyStyle>')
        self._kmls.append('</Style>')

    def closeKml(self):
        self._kmls.append('</Document>')
        self._kmls.append('</kml>')

    def initPoly(self, style, cnt):
        self._kmls.append('<Placemark id="%s_%d">' % (style, cnt))
        self.addProperty('styleUrl', '#%s' % (style))
        self._kmls.append('<Polygon>')

    def addPoly(self, poly):
        self._kmls.append('<outerBoundaryIs>')
        self.addLinearRing(poly.exterior_ring)
        self._kmls.append('</outerBoundaryIs>')
        for i in range(poly.num_interior_rings):
            self._kmls.append('<innerBoundaryIs>')
            self.addLinearRing(poly[1+i])
            self._kmls.append('</innerBoundaryIs>')

    def addLinearRing(self, lr):
        self._kmls.append('<LinearRing>')
        self._kmls.append('<coordinates>')
        for cords in lr:
            self._kmls.append('%f,%f' % (cords[0], cords[1]))
        self._kmls.append('</coordinates>')
        self._kmls.append('</LinearRing>')

    def closePoly(self):
        self._kmls.append('</Polygon>')
        self._kmls.append('</Placemark>')

    def addProperty(self, tag, value):
        # note that 'color' and 'styleUrl' tags are whitespace-sensitive
        self._kmls.append('<%s>%s</%s>' % (tag, value, tag))
            

