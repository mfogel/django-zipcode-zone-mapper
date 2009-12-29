django-zone-mapper

This apps builds a kml file for you with different zones as different
colors of your choosing.  The zones are built out of zcta's, a census
bureau approximation of a zip code.

This app relies heavily on the django.contrib.gis module.

Two commands.  'loadTigerData' is to be run first, then 'buildKml' can be
ran multiple times.

 1. ./manage.py loadTigerData <path to tiger data shape file>

    The tiger data shape file is a public file provided by the census.  For
    example, the 2009 one is available in the zip file:

    http://www2.census.gov/geo/tiger/TIGER2009/tl_2009_us_zcta5.zip

    In that zip file there is a file named tl_2009_us_zcta5.shp.  That's
    what you're looking for.

    Running this command loads the needed zcta's into your database.

 2. ./manage.py buildKml > name_me.kml

    This command builds the kml file you want from the zcta's in your
    database, and pushes the result to standard out.

