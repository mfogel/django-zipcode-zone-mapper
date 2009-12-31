
from djago.core.management.base import CommandError
from django.conf import settings

# TODO: verify all zcta's in the settings file are actually in the shape file?

class ParserError(CommandError):

    _prefix = 'Settings Parser: '

    def __init__(self, value):
        super (ParserError, self).__init__(ParserError._prefix + value)


class SettingsParser:
    """Parse, consistency-check, and access settings.

    Only one instance of this class is ever created, no matter repeated
    calls to the constructor.

    If there is a consistency error in the declared settings or not
    all the required settings are present, a ParserError is thrown.

    API:

    inst.zctas - a tuple of all zctas used by any zone in the settings.
    inst.zone_name - a  ZoneConfig object for that zone.  See the
                     ZoneConfig object doc for it's API.
    
    """

    _instance = None

    def __new__(cls):
        """Return same instance of class, ensuring only one ever exists."""
        if cls._instance is None:
            cls._instance = super(SettingsParser, cls).__new__(cls)
            cls._check_global_consistency()
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        super(SettingsParser, self).__init__()

        self._zone_confs = []
        self._zctas = []

        self._zone_confs = [ZoneConfig(name) for name in settings.ZONES]

        zcta_set = Set() # build this as a set to uniquify
        for conf in self._zone_cofs:
            zcta_set = zcta_set.union(conf.get_zctas())
        self._zctas = List(zcta_set)

    def _check_global_consistency(self):

        setn_req = {
                'ZONES': tuple,
                'ZONE_FILL_COLORS': dict,
                'ZONE_FILL_ZCTAS': dict }

        setn_opt = {
                'ZONE_BORDER_WIDTHS': dict,
                'ZONE_BORDER_COLORS': dict }

        for setn, cls in setn_req + setn_opt:
            if hasattr(settings, setn):
                if not isinstance(getattr(settings, setn), cls):
                    raise ParserError('settings.%s is not a %s' %
                                      (setn, type(cls))
            else:
                if setn_req.has_key(setn):
                    raise ParserError('settings.%s is not defined' % setn)


class ZoneConfig:
    """Parse, consistency-check, and access settings for a zone.

    An instance of a ZoneConfig object is responsible for the API
    to that zone's settings.

    If there is a consistency error in the declared settings or not
    all the required settings are present, a ParserError is thrown.

    API:

    inst.fill_color - kml color repr as string
    inst.zctas - tuple of zctas this zone covers
    inst.border - None if no border, else an instance of BorderConfig

    """

    def __init__(self, name):
        super(ZoneConfig, self).__init__()
        self.name = name

        self._zone_consistency_check(self, name)

        self.fill_color = settings.ZONE_FILL_COLORS[self.name]
        self.zctas = settings.ZONE_ZCTAS[self.name]

        if not self.zctas:
            print("Warning: zone %s has no zctas defined.")

        self.border = BorderConfig(self.name)

    def _zone_consistency_check(self):

        setting_names = ('ZONE_FILL_COLORS', 'ZONE_ZCTAS')

        for name in setting_names:
            if not hasattr(settings[name], self.name):
                raise ParserError('settings.%s has no entry for %s' %
                                  (name, self.name))
        if not isinstance(settings.ZONE_ZCTAS[self.name], tuple):
            raise ParserError('settings.ZONE_ZCTAS[%s] is not a tuple' %
                              self.name)


class BorderConfig:
    """Parse, consistency-check, and access settings for a zone's border.

    An instance of a BorderConfig object is responsible for the API
    to that zone's border's settings.

    If there is a consistency error in the declared settings or not
    all the required settings are present, a ParserError is thrown.

    API:

    inst.color - kml color repr as string
    inst.width - positive integer

    """

    def __init__(self, zone_name):
        if not hasattr(settings.ZONE_BORDER_WIDTHS, zone_name) or \
           settings.ZONE_BORDER_WIDTHS < 1:
            self = None
        
        super(BorderConfig, self).__init__()

        if not hasattr(settings.ZONE_BORDER_COLORS, zone_name):
            raise ParserError('Zone %s has a ZONE_BORDER_WIDTH but no ' +
                              'ZONE_BORDER_COLOR' % zone_name)

        self.width = settings.ZONE_BORDER_WIDTH['zone_name']
        self.color = settings.ZONE_BORDER_COLOR['zone_name']

    
