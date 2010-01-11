
import re
import sys
from warnings import warn

from django.core.management.base import NoArgsCommand

from zone_mapper.models import Zone

class Command(NoArgsCommand):

    help = "Builds the KML file for the current database contents.  Output to stdout."

    def handle_noargs(self, **options):

        kml = Kml()

        for zone in Zone.objects.all():
            # print warnings if some of our ZipCodes have no shp info
            for zipcode in zone.orphan_zipcodes():
                warn(("ZipCode %s associated with Zone %s but has no " +
                      "shape info. Need to reload tiger data?"
                      ) % (zipcode, zone), RuntimeWarning)

            multipoly = zone.multipoly()
            if not multipoly:
                continue
            kml.add_style(zone.name, zone.fill_color, zone.border_width,
                         zone.border_color)
            for poly in multipoly:
                kml.add_poly(poly, zone.name)

        kml.close()
        kml.write(sys.stdout)

class Kml:

    # stuff to format indenting nicely
    _one_indent = '  '
    _indent_n_skip = 3 # don't indent first # of open tags
    _re_tagopen = re.compile('^<[^/]')
    _re_tagclose = re.compile('^</')
    _re_tagboth = re.compile('<[^/].*>.*</.*>$')

    def __init__(self):
        self._cur_indent = 0 - Kml._indent_n_skip
        self._lines = []
        self._lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        self._lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        self._lines.append('<Document>')

    def close(self):
        self._lines.append('</Document>')
        self._lines.append('</kml>')

    def write(self, fh):
        for line in self._lines:
            self._write_line(line, fh)

    def _write_line(self, line, fh):
        if Kml._re_tagclose.match(line):
            self._cur_indent -= 1
        fh.write(Kml._one_indent * self._cur_indent)
        if not Kml._re_tagboth.match(line) and Kml._re_tagopen.match(line):
            self._cur_indent += 1
        fh.write(line)
        fh.write('\n')

    def add_style(self, name, fill_color, border_width=0, border_color=None):
        self._lines.append('<Style id="%s">' % (name))

        if border_width > 0:
            self._lines.append('<LineStyle>')
            self.add_property('width', border_width)
            if border_color is None:
                border_color = fill_color
            self.add_property('color', border_color)
            self._lines.append('</LineStyle>')

        self._lines.append('<PolyStyle>')
        self.add_property('color', fill_color)
        self._lines.append('</PolyStyle>')

        self._lines.append('</Style>')

    def add_poly(self, poly, style):
        self._lines.append('<Placemark>')
        self.add_property('styleUrl', '#%s' % (style))
        self._lines.append('<Polygon>')
        self._lines.append('<outerBoundaryIs>')
        self.add_linear_ring(poly.exterior_ring)
        self._lines.append('</outerBoundaryIs>')
        for i in range(poly.num_interior_rings):
            self._lines.append('<innerBoundaryIs>')
            self.add_linear_ring(poly[1+i])
            self._lines.append('</innerBoundaryIs>')
        self._lines.append('</Polygon>')
        self._lines.append('</Placemark>')

    def add_linear_ring(self, lr):
        self._lines.append('<LinearRing>')
        self._lines.append('<coordinates>')
        for cords in lr:
            self._lines.append('%f,%f' % (cords[0], cords[1]))
        self._lines.append('</coordinates>')
        self._lines.append('</LinearRing>')

    def add_property(self, tag, value):
        # note that 'color' and 'styleUrl' tags are whitespace-sensitive
        self._lines.append('<%s>%s</%s>' % (tag, value, tag))


