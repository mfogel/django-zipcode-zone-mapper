
import re
import sys
from warnings import warn
from xml.etree import ElementTree as ET

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

        kml.write(sys.stdout)

class Kml:

    # stuff to format indenting nicely
    _indent_step = '  '
    _indent_n_skip = 3 # don't indent first # of open tags
    _re_tagopen = re.compile('^<[^/]')
    _re_tagclose = re.compile('^</')
    _re_tagboth = re.compile('<[^/].*>.*</.*>$')

    _kml_xmlns = "http://www.opengis.net/kml/2.2"

    def __init__(self):
        self._cur_indent = 0 - Kml._indent_n_skip
        self._lines = []
        # FIXME: can't ElementTree handle this xml namespace decl gracefully?
        self._kml_elm = ET.Element('kml', {'xmlns': Kml._kml_xmlns})
        self._doc_elm = ET.SubElement(self._kml_elm, 'Document')
        self._tree = ET.ElementTree(self._kml_elm)

    def write(self, fh):
        # FIXME: someway to get ElementTree to do this?
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.indent(self._kml_elm)
        self._tree.write(fh)

    def indent(self, elem, level=0):
        # adpted this from http://infix.se/2007/02/06/gentlemen-indent-your-xml
        i = "\n" + level * Kml._indent_step
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + Kml._indent_step
            for e in elem:
                self.indent(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + Kml._indent_step
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i 
        # one off the <coordinates> formatting
        if elem.tag == 'coordinates':
            elem.text = elem.text.replace("\n", i + Kml._indent_step)
            elem.text = elem.text[:-len(Kml._indent_step)]

    def _write_line(self, line, fh):
        if Kml._re_tagclose.match(line):
            self._cur_indent -= 1
        fh.write(Kml._one_indent * self._cur_indent)
        if not Kml._re_tagboth.match(line) and Kml._re_tagopen.match(line):
            self._cur_indent += 1
        fh.write(line)
        fh.write('\n')

    def add_style(self, name, fill_color, border_width=0, border_color=None):
        style_elm = ET.SubElement(self._doc_elm, 'Style', {'id': name})

        if border_width > 0:
            linestyle_elm = ET.SubElement(style_elm, 'LineStyle')
            self.add_simple_child_tag(linestyle_elm, 'width', border_width)
            if border_color is None:
                border_color = fill_color
            self.add_simple_child_tag(linestyle_elm, 'color', border_color)

        polystyle_elm = ET.SubElement(style_elm, 'PolyStyle')
        self.add_simple_child_tag(polystyle_elm, 'color', fill_color)

    def add_poly(self, poly, style):
        placemark_elm = ET.SubElement(self._doc_elm, 'Placemark')
        self.add_simple_child_tag(placemark_elm, 'styleUrl', '#%s' % style)
        poly_elm = ET.SubElement(placemark_elm, 'Polygon')
        outer_elm = ET.SubElement(poly_elm, 'outerBoundaryIs')
        self.add_linear_ring(outer_elm, poly.exterior_ring)
        for i in range(poly.num_interior_rings):
            inner_elm = ET.SubElement(poly_elm, 'innerBoundaryIs')
            self.add_linear_ring(inner_elm, poly[1+i])

    def add_linear_ring(self, parent_elm, ring):
        ring_elm = ET.SubElement(parent_elm, 'LinearRing')
        cords_elm = ET.SubElement(ring_elm, 'coordinates')
        cords_elm.text = '\n'
        for cords in ring:
            cords_elm.text += '%f,%f\n' % (cords[0], cords[1])

    def add_simple_child_tag(self, parent_elm, tagname, tagtext):
        child = ET.SubElement(parent_elm, tagname)
        child.text = '%s' % tagtext

