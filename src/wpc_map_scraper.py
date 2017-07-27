"""
This program downloads historical weather maps from the Weather Prediction Center (WPC) that is part of the
National Weather Service.  Surface weather maps for North America and the Continental United States are
available from May 1, 2005 onward.  Eight different kinds of maps are available at eight different times per day.
This program will allow you to download one type of map for a range of dates, and store the maps in a folder.
"""

import requests
import shutil
import sys
from bs4 import BeautifulSoup
import iso8601
from datetime import datetime, timezone, timedelta   # like it says
import os.path
from urllib.parse import urljoin
import time
import click

# constants to simplify maintenance
SITE_URL = 'http://www.wpc.ncep.noaa.gov/'
PAGE_URL = 'archives/web_pages/sfc/sfc_archive_maps.php?'
MAP_DIR = '~/Desktop/Maps'  # directory to save the downloaded maps
IMAGE_FILE_TYPE = 'gif'
MAP_CSS_SELECTOR = '.sfcmapimage'  # CSS class selector for the weather map
WAIT_PERIOD = 5     # time in seconds to wait before downloading the next map.


@click.command()
@click.option('--start-date', help='Starting date as YYYY-MM-DD or YYYYMMDD format. ')
@click.option('--end-date',   help='Ending date as YYYY-MM-DD or YYYYMMDD format')
@click.option('--delta-hours', default=24, type=click.Choice([3, 6, 12, 24]), help='Hours between subsequent map downloads (3, 6, 12, 24)')
@click.option('--map-types', 'transformed', flag_value='lower',
              multiple=True,
              type=click.Choice(['namussfc', 'usfntsfc', 'print_us', 'ussatsfc', 'radsfcus_exp', 'namfntsfc', 'na_zoomin', 'satsfcnps']),
              help='Type(s) of surface weather maps to download')
@click.option('-md', '--map-dir', help="Directory to store downloaded maps. Defaults to a Map directory on the user's desktop")
def get_map(start_date, end_date, delta_hours, map_types, map_dir):
    """
    Downloads and saves a series of weather map images to disk.

    One map of each type will be downloaded for every date and time specified.
    :param start_date:  Starting data and time (inclusive)
    :param end_date:    Stopping date and time (inclusive)
    :param delta_hours: Number of hours between subsequent downloads.  Valid values are: 0, 6, 12, 18.  All times are UTC or 'Z'
    :param map_types:   Valid map types include following strings:
        namussfc        Unites States (CONUS)
        usfntsfc        United States (Fronts/Analysis Only)
        print_us        United States (B/W)
        ussatsfc        U.S. Analysis/Satellite Composition
        radsfcus_exp    U.S. Analysis/Radar Composition
        namfntsfc       North America (Fronts/Analysis Only)
        satsfcnps       North America Analysis/Satellite Composition
    :param map_dir:     Folder used to store the downloaded map files
    """
    print('start_date:', start_date)
    print('end_date:', end_date)
    print('delta_hours:', delta_hours)
    print('map_types:', map_types)
    print('map_dir:', map_dir)
    times = _make_times(delta_hours)
    print('times:', times)
    dt_series = _make_time_series(start_date, end_date, times)
    for dt in dt_series:
        for map_type in map_types:
            page_url = _build_page_url(dt, map_type)
            map_path = _get_map_path(map_dir, dt, map_type)
            image_url = _build_image_url(page_url)
            _download_map(image_url, map_path)
            time.sleep(WAIT_PERIOD)


def _build_page_url(date_and_time, map_type):
    """
    Makes the url of the page that contains the archived surface weather map.

    :param date_and_time: The datetime for the map
    :param map_type: The type of surface map to download
    :returns The url for the surface map page with the date, time and map type correctly formatted

    >>> import wpc_map_scraper as wpc
    >>> map_time = wpc.datetime(year=2017, month=7, day=4, hour=6, tzinfo=timezone.utc)

    >>> wpc._build_page_url(map_time, 'namussfc')
    'http://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive_maps.php?arcdate=07/04/2017&selmap=201707046&maptype=namussfc'
    """
    year, month, day, hour = date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour
    return f'{SITE_URL}{PAGE_URL}arcdate={month:02d}/{day:02d}/{year}&selmap={year}{month:02d}{day:02d}{hour}&maptype={map_type}'


def _make_iso_date(date_str, time_str='00'):
    """
    Makes and parses an ISO8601 compliant date string into a datetime object.

    All times are in Universal Coordinated Time (UTC) which is commonly referred to a Z or 'Zulu'
    :param date_str: Valid date strings that have the form: YYYY-MM-DD or YYYYMMDD
    :param time_str: Valid times include: 0, 6, 12, 18. All times are UTC or 'Z'.  Defaults to OZ
    :return: The datetime object for the specified date and time for the UTC time zone

    >>> import wpc_map_scraper as wpc

    >>> wpc._make_iso_date('2017-07-04')
    datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>)

    >>> wpc._make_iso_date('2017-07-04', time_str='12')
    datetime.datetime(2017, 7, 4, 12, 0, tzinfo=<iso8601.Utc>)
    """
    iso_str = date_str + 'T' + time_str + 'Z'
    return iso8601.parse_date(iso_str)


def _make_time_series(begin, end, times=None):
    """
    Makes the series of datetime objects for the period of interest.

    :param begin: Starting date for the date range (inclusive)
    :param end: Ending date (inclusive) for the date range
    :param times: List of times for daily maps (defaults to '00')
    :return: A list of datetime objects for each time and every day specified in the range

    >>> import wpc_map_scraper as wpc

    >>> wpc._make_time_series('2017-07-04', '2017-07-05')
    [datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>), datetime.datetime(2017, 7, 5, 0, 0, tzinfo=<iso8601.Utc>)]

    >>> wpc._make_time_series('2017-07-04', '2017-07-04', times=['00', '12'])
    [datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>), datetime.datetime(2017, 7, 4, 12, 0, tzinfo=<iso8601.Utc>)]
    """
    # create the starting and ending datetime objects using values provided on the command line
    start_dt = _make_iso_date(begin)
    stop_dt = _make_iso_date(end)
    num_days = (stop_dt - start_dt).days  # timedelta object has a days attribute

    # reality check
    if start_dt > stop_dt:
        return []

    # build default time list
    if not times:
        times = ['00']

    # build a list of datetime objects by adding incremental day and time offsets to the start date
    # note: range(value) is generates values from 0 to value - 1, therefore adding 1
    return [
        start_dt + timedelta(days=d, hours=int(t))
        for d in range(num_days+1)
        for t in times]


def _get_map_path(map_dir, dt, map_type):
    """
    Makes the absolute path for the weather map image file.

    :param map_dir: Path to storage directory as a string
    :param dt: Datetime of the map
    :param map_type: The type of surface map to download
    :return: Absolute path for the weather map image file

    >>> import wpc_map_scraper as wpc
    >>> dt = datetime(2017, 7, 4, 12, 0, tzinfo=iso8601.UTC)

    >>> wpc._get_map_path('~/Desktop/Wx_Maps', dt, 'namussfc')
    '/Users/rob/Desktop/Wx_Maps/20170704_12z_namussfc.gif'
    """
    # name and create needed directory tree
    if map_dir:
        map_path = os.path.expanduser(map_dir)
    else:
        map_path = os.path.join(os.path.expanduser(map_dir), MAP_DIR)

    # recursively create the directory tree
    os.makedirs(map_path, exist_ok=True)

    filename = f'{dt.year:04d}{dt.month:02d}{dt.day:02d}_{dt.hour:02d}z_{map_type}'
    filepath = os.path.join(os.path.abspath(map_path), filename + os.path.extsep + IMAGE_FILE_TYPE)
    return os.path.abspath(filepath)


def _build_image_url(page_url):
    """
    Constructs the URL of weather map image found within the page.

    :param page_url: The full url of the page containing the map
    :return: The URL of the weather map image
    :exception: Any exception that occurs making the HTTP request
    """
    #  get url to the weather map image from the DOM and do so looking like a browser, not a scraper
    resp = requests.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    map_element = soup.select('.sfcmapimage')   # CSS class selector

    image_url = None
    if map_element:
        rel_image_path = map_element[0].get('src')
        # form the complete url for the image
        image_url = urljoin(urljoin(SITE_URL, PAGE_URL), rel_image_path)
    else:
        print('Could not find map image', file=sys.stderr)

    return image_url


def _download_map(image_url, map_file_path):
    """
    Downloads the weather map image and stores it as a local file.

    :param image_url: The url of the weather map image
    :param map_file_path: The absolute path to store the image file
    :return: True if the map was downloaded and successfully stored on disk, otherwise, False
    :exception: Any exception that occurs making the HTTP request or IOError from storing the file on disk
    """

    # get the map while appearing as a browser
    resp = requests.get(image_url, stream=True)
    resp.decode_content = True
    resp.raise_for_status()

    # save the map
    with open(map_file_path, '+wb') as fout:
        # copy the image to a file and have shutil handle the details
        shutil.copyfileobj(resp.raw, fout)


def _make_times(delta_hours):
    """
    Creates the list of times that a map will be downloaded for each day starting a '00' UTC.

    :param delta_hours: The change in hours between subsequent maps
    :return: The list of times represented as list of strings

    >>> _make_times(6)
    ['00', '06', '12', '18']
    """
    return [f'{t:02d}' for t in range(0, 24, delta_hours)]


