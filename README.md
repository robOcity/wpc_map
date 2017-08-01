# Wx-Map

### Downloads archived surface weather maps from the Weather Prediction Center

The Weather Prediction Center -- part of the National Weather Service --
has an large number of surface weather maps available to download.  For getting a few maps, visiting the [Weather Prediction Center](http://www.wpc.ncep.noaa.gov/index.shtml#page=ovw)
site works quite well, if you need download a sequence of maps, that is what Wx-Map is written for.  Specifically, Wx_Map downloads weather maps from the
[WPC's Surface Analysis Archive](http://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive.php)
page.

### Running Wx-Map

Wx_Map is a command line tool implemented in Python.  Here is how to use it.

#### *Getting help*
  ```bash
  $ python wx_map.py -h
  Usage: wx_map.py [OPTIONS]

    Downloads and saves a series of weather maps from the Weather Prediction
    Centers Surface Analysis Archive.

    One map of each type will be downloaded for every date and time specified.

    :param start_date:  Starting data and time (inclusive)
    :param end_date:    Stopping date and time (inclusive)
    :param period:      Hours between subsequent maps, first map is always 00Z. Valid values are: 3, 6, 12, or 24.
    :param maps:        Valid map types include following strings:
        namussfc        Unites States (CONUS)
        usfntsfc        United States (Fronts/Analysis Only)
        print_us        United States (B/W)
        ussatsfc        U.S. Analysis/Satellite Composition
        radsfcus_exp    U.S. Analysis/Radar Composition
        namfntsfc       North America (Fronts/Analysis Only)
        satsfcnps       North America Analysis/Satellite Composition
    :param map_dir:     Folder used to store the downloaded map files

  Options:
    -s, --start_date TEXT           Starting date as YYYY-MM-DD or YYYYMMDD
                                    format.
    -e, --end_date TEXT             Ending date as YYYY-MM-DD or YYYYMMDD format
    -p, --period [3|6|12|24]        Hours between subsequent maps (3, 6, 12,
                                    24).  First map is always 00Z.  The period
                                    default is 24.
    -m, --maps [namussfc|usfntsfc|print_us|ussatsfc|radsfcus_exp|namfntsfc|satsfcnps]
                                    Type(s) of surface weather maps to download.
                                    Repeat this option to specify several
                                    different types of maps.
    -d, --map_dir TEXT              Directory to store downloaded maps. Defaults
                                    to ~/Desktop/Wx_Maps and the path is
                                    normalized for operating system.
    -h, --help                      Show this message and exit.
  ```

#### *Downloading a single map for one day*
  ```bash
  $ python wx_map.py -s 2017-07-04 -e 2017-07-04 -m namussfc
  [####################################]  100%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_namussfc.gif
  ```

#### *Downloading a several types of maps of files for one day*
  ```bash
  $ python wx_map.py -s 2017-07-04 -e 2017-07-04 -m namussfc -m print_us -m ussatsfc
  [############------------------------]   33%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_namussfc.gif
  [########################------------]   66%  0d 00:00:04
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_print_us.gif
  [####################################]  100%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_ussatsfc.gif
  ```

#### *Downloading one map every 6 hours for one day*
  ```bash
  $ python wx_map.py -s 2017-07-04 -e 2017-07-04 -p 6 -m satsfcnps
    [#########---------------------------]   25%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_satsfcnps.gif
    [##################------------------]   50%  0d 00:00:07
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_06z_satsfcnps.gif
    [###########################---------]   75%  0d 00:00:04
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_12z_satsfcnps.gif
    [####################################]  100%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_18z_satsfcnps.gif
  ```

#### *Downloading one map for a range of days every 12 hours*
  ```bash
  $ python wx_map.py -s 2017-07-04 -e 2017-07-07 -p 12 -m namussfc
    [####--------------------------------]   12%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_namussfc.gif
    [#########---------------------------]   25%  0d 00:00:18
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_12z_namussfc.gif
    [#############-----------------------]   37%  0d 00:00:18
  Saving file: /Users/rob/Desktop/Wx_Maps/20170705_00z_namussfc.gif
    [##################------------------]   50%  0d 00:00:15
  Saving file: /Users/rob/Desktop/Wx_Maps/20170705_12z_namussfc.gif
    [######################--------------]   62%  0d 00:00:13
  Saving file: /Users/rob/Desktop/Wx_Maps/20170706_00z_namussfc.gif
    [###########################---------]   75%  0d 00:00:10
  Saving file: /Users/rob/Desktop/Wx_Maps/20170706_12z_namussfc.gif
    [###############################-----]   87%  0d 00:00:05
  Saving file: /Users/rob/Desktop/Wx_Maps/20170707_00z_namussfc.gif
    [####################################]  100%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170707_12z_namussfc.gif
  ```

#### *Downloading two maps for a range of days every 12 hours*
  ```bash
  $ python wx_map.py -s 2017-07-04 -e 2017-07-07 -p 12 -m namussfc
    [####--------------------------------]   12%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_00z_namussfc.gif
    [#########---------------------------]   25%  0d 00:00:18
  Saving file: /Users/rob/Desktop/Wx_Maps/20170704_12z_namussfc.gif
    [#############-----------------------]   37%  0d 00:00:18
  Saving file: /Users/rob/Desktop/Wx_Maps/20170705_00z_namussfc.gif
    [##################------------------]   50%  0d 00:00:15
  Saving file: /Users/rob/Desktop/Wx_Maps/20170705_12z_namussfc.gif
    [######################--------------]   62%  0d 00:00:13
  Saving file: /Users/rob/Desktop/Wx_Maps/20170706_00z_namussfc.gif
    [###########################---------]   75%  0d 00:00:10
  Saving file: /Users/rob/Desktop/Wx_Maps/20170706_12z_namussfc.gif
    [###############################-----]   87%  0d 00:00:05
  Saving file: /Users/rob/Desktop/Wx_Maps/20170707_00z_namussfc.gif
    [####################################]  100%
  Saving file: /Users/rob/Desktop/Wx_Maps/20170707_12z_namussfc.gif
  ```
