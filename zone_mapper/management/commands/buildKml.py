
import re
from sys import stdout
from warnings import warn

from django.core.management.base import NoArgsCommand

from zone_mapper.models import Zone

class Command(NoArgsCommand):

    help = "Builds the KML file for the current contents of the deliveryMap zcta database.  Output to stdout."

    # stuff for 'verbose' mode to format indenting nicely
    _one_indent = '  '
    _indent_n_skip = 3 # don't indent first # of open tags
    _re_tagopen = re.compile('^<[^/]')
    _re_tagclose = re.compile('^</')
    _re_tagboth = re.compile('<[^/].*>.*</.*>$')

    def handle_noargs(self, **options):

        self.initKml()

        for zone in Zone.objects.all():
            # print warnings if some of our ZipCodes have no shp info
            for zipcode in zone.orphan_zipcodes():
                warn(("ZipCode %s associated with Zone %s but has no " +
                      "shape info. Need to reload tiger data?"
                      ) % (zipcode, zone), RuntimeWarning)

            multipoly = zone.multipoly()
            if not multipoly:
                continue
            self.addStyle(zone.name, zone.fill_color, zone.border_width,
                          zone.border_color)
            for poly in multipoly:
                self.initPoly(zone.name)
                self.addPoly(poly)
                self.closePoly()

        self.closeKml()
        self.printKml(verbose=True)

    def printKml(self, verbose=False):
        for line in self._kmls:
            self.writeLine(line, verbose)

    def writeLine(self, line, verbose=False):
        if verbose:
            if Command._re_tagclose.match(line):
                self._cur_indent -= 1
            stdout.write(Command._one_indent * self._cur_indent)
            if Command._re_tagboth.match(line):
                pass
            elif Command._re_tagopen.match(line):
                self._cur_indent += 1

        stdout.write(line)
        stdout.write('\n')

    def initKml(self):
        self._cur_indent = 0 - Command._indent_n_skip
        self._kmls = []
        self._kmls.append('<?xml version="1.0" encoding="UTF-8"?>')
        self._kmls.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        self._kmls.append('<Document>')

    def addStyle(self, name, fill_color, border_width=0, border_color=None):
        self._kmls.append('<Style id="%s">' % (name))

        if border_width > 0:
            self._kmls.append('<LineStyle>')
            self.addProperty('width', border_width)
            if border_color is None:
                border_color = fill_color
            self.addProperty('color', border_color)
            self._kmls.append('</LineStyle>')

        self._kmls.append('<PolyStyle>')
        self.addProperty('color', fill_color)
        self._kmls.append('</PolyStyle>')

        self._kmls.append('</Style>')

    def closeKml(self):
        self._kmls.append('</Document>')
        self._kmls.append('</kml>')

    def initPoly(self, style):
        self._kmls.append('<Placemark>')
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
            

