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

 2. ./manage.py buildkml > name_me.kml

    This command builds the kml file you want from the zcta's in your
    database, and pushes the result to standard out.

