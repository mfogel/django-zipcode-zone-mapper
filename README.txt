django-zipcode-zone-mapper

This apps builds a kml file for you with different zones as different
colors of your choosing.  The zones are built out of zcta's, a census
bureau approximation of a zip code.

This app relies heavily on the django.contrib.gis module.

General workflow to get started:

 - add zone_mapper to your INSTALLED_APPS django setting
 - run ./manage.py syncdb
 - navigate to django admin/zone_mapper
 - configure a 'zone' or two (fill color, border width and color)
 - configure a number of 'zipcodes' and associate them with a existing 'zone'
 - run ./manage.py loadtigerdata
 - run ./manage.py buildkml

More detail on the two commands:

 1. ./manage.py loadtigerdata <path to tiger data shape file>

    The tiger data shape file is a public file provided by the census.  For
    example, the 2009 one is available in the zip file:

    http://www2.census.gov/geo/tiger/TIGER2009/tl_2009_us_zcta5.zip

    In that zip file there is a file named tl_2009_us_zcta5.shp.  That's
    what you're looking for.

    Running this command loads the needed zcta's into your database.

 2. ./manage.py buildkml [-z] <fileout, usually *.km(l|z)>

    This command builds the kml file you want from the zcta's in your
    database.  If the '-z' option is set, output is compressed with zlib.
    This is good if you want to make a .kmz file.

