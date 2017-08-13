"""
Download a sequence of archived weather maps from the Weather Prediction Center (WPC).

Surface weather maps for North America and the Continental United States are
available from May 1, 2005 onward.  Eight different kinds of maps are available at eight different times each day.
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
from collections import namedtuple

# globals
MAP_DIR = '~/Desktop/Wx_Maps'      # directory to save the downloaded maps
SITE_URL = 'http://www.wpc.ncep.noaa.gov/'
PAGE_URL = 'archives/web_pages/sfc/sfc_archive_maps.php?'
IMAGE_FILE_TYPE = 'gif'            # format used by WPC
MAP_CSS_SELECTOR = '.sfcmapimage'  # CSS class selector for the weather map
WAIT_PERIOD = 5                    # value in seconds between downloads (be kind its a resource we all share)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

Plan = namedtuple('Plan', 'page_url, map_path')


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-s', '--start_date', help='Starting date as YYYY-MM-DD or YYYYMMDD format. ')
@click.option('-e', '--end_date',   help='Ending date as YYYY-MM-DD or YYYYMMDD format')
# Note: click.Choice 6.x does not support integers, only strings
@click.option('-p', '--period', type=click.Choice(['3', '6', '12', '24']), default='24',
              help='Hours between subsequent maps (3, 6, 12, 24).  First map is always 00Z.  The period default is 24.')
@click.option('-m', '--maps', multiple=True,
              type=click.Choice(['namussfc', 'usfntsfc', 'print_us', 'ussatsfc', 'radsfcus_exp', 'namfntsfc', 'satsfcnps']),
              help='Type(s) of surface weather maps to download.  Repeat this option to specify several different types of maps.')
@click.option('-d', '--map_dir', default=MAP_DIR,
              help="Directory to store downloaded maps. Defaults to {} and the path is normalized for operating system.".format(MAP_DIR))
def get(start_date, end_date, period, maps, map_dir):
    """Downloads and saves a series of weather maps from the Weather Prediction Center's Surface Analysis Archive.

    \b
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
    """
    # Note: \b in the above docstring forces click to maintain the formatting the docstring above

    plans = []
    date_times = _make_time_series(start_date, end_date, period)
    for dt in date_times:
        for map_type in maps:
            page_url = _build_page_url(dt, map_type)
            map_path = _get_map_path(map_dir, dt, map_type)
            plans.append(Plan(page_url=page_url, map_path=map_path))

    # TODO ask the user if what they requested is really what they want
    #click.secho('wpc_map\nNumber of maps to download: {}\n{}'.format(len(dt_series), dt_series))

    with click.progressbar(plans) as bar:
        for plan in bar:
            # commence scrapping
            image_url = _scan_page_for_map(plan.page_url)
            _download_map_from_page(image_url, plan.map_path)
            click.secho('\nSaving file: {}'.format(plan.map_path))
            time.sleep(WAIT_PERIOD)


def _build_page_url(date_and_time, map_type):
    """
    Makes the url of the page that contains the archived surface weather map.

    :param date_and_time: The datetime for the map
    :param map_type: The type of surface map to download
    :returns The url for the surface map page with the date, time and map type correctly formatted

    >>> from wpc_map import cli
    >>> map_time = cli.datetime(year=2017, month=7, day=4, hour=6, tzinfo=timezone.utc)

    >>> cli._build_page_url(map_time, 'namussfc')
    'http://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive_maps.php?arcdate=07/04/2017&selmap=2017070406&maptype=namussfc'
    """
    year, month, day, hour = date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour
    return f'{SITE_URL}{PAGE_URL}arcdate={month:02d}/{day:02d}/{year}&selmap={year}{month:02d}{day:02d}{hour:02d}&maptype={map_type}'


def _make_iso_date(date_str, hour_str='00'):
    """
    Makes and parses an ISO8601 compliant date string into a datetime object.

    All times are in Universal Coordinated Time (UTC) which is commonly referred to a Z or 'Zulu'
    :param date_str: Valid date strings that have the form: YYYY-MM-DD or YYYYMMDD
    :param hour_str: Valid times include: 0, 3, 6, 12, 24. All times are UTC or 'Z'.  Defaults to OZ
    :return: The datetime object for the specified date and time for the UTC time zone

    >>> from wpc_map import cli

    >>> cli._make_iso_date('2017-07-04')
    datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>)

    >>> cli._make_iso_date('2017-07-04', hour_str='12')
    datetime.datetime(2017, 7, 4, 12, 0, tzinfo=<iso8601.Utc>)
    """
    iso_str = date_str + 'T' + hour_str + 'Z'
    return iso8601.parse_date(iso_str)


def _build_daily_map_times(period):
    """
    Create the list of daily map times.

    Starting with the 0Z map and adding others for each period throughout the day.
    :param period: The time between subsequent maps (3, 6, 12)
    :return: The list of requested map times.

    >>> from wpc_map import cli

    >>> cli._build_daily_map_times('6')
    [0, 6, 12, 18]
    """
    period = int(period)
    return [period * n
            for n in range(24 // period)]


def _make_time_series(start_date, end_date, period='24'):
    """
    Makes the series of datetime objects for the period of interest.

    :param begin: Starting date for the date range (inclusive)
    :param end: Ending date (inclusive) for the date range
    :param period: The time between subsequent maps (defaults to '00')
    :return: A list of datetime objects from the start date at 0Z to the end date with maps for each period specified.

    >>> from wpc_map import cli

    >>> cli._make_time_series('2017-07-04', '2017-07-04')
    [datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>)]

    >>> cli._make_time_series('2017-07-04', '2017-07-05')
    [datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>), datetime.datetime(2017, 7, 5, 0, 0, tzinfo=<iso8601.Utc>)]

    >>> cli._make_time_series('2017-07-04', '2017-07-04', period='12')
    [datetime.datetime(2017, 7, 4, 0, 0, tzinfo=<iso8601.Utc>), datetime.datetime(2017, 7, 4, 12, 0, tzinfo=<iso8601.Utc>)]
    """
    # create the starting and ending datetime objects using values provided on the command line
    start_dt = _make_iso_date(start_date)
    stop_dt = _make_iso_date(end_date)
    num_days = (stop_dt - start_dt).days  # timedelta object has a days attribute

    # reality check
    if start_dt > stop_dt:
        return []

    return [
        start_dt + timedelta(days=d, hours=int(t))
        for d in range(num_days+1)
        for t in _build_daily_map_times(period)
    ]


def _get_map_path(map_dir, dt, map_type):
    """
    Makes the absolute path for the weather map image file.

    :param map_dir: Path to storage directory as a string
    :param dt: Datetime of the map
    :param map_type: The type of surface map to download
    :return: Absolute path for the weather map image file

    >>> from wpc_map import cli
    >>> dt = datetime(2017, 7, 4, 12, 0, tzinfo=iso8601.UTC)

    >>> cli._get_map_path('~/Desktop/Wx_Maps', dt, 'namussfc')
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


def _scan_page_for_map(page_url):
    """
    Constructs the URL of weather map image found within the page.

    :param page_url: The full url of the page containing the map
    :return: The URL of the weather map image
    :exception: Any exception that occurs making the HTTP request
    """
    #  get url to the weather map image from the DOM and do so looking like a browser, not a scraper
    resp = requests.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    map_element = soup.select('.sfcmapimage')   # CSS class selector

    image_url = None
    if map_element:
        rel_image_path = map_element[0].get('src')
        # form the complete url for the image
        image_url = urljoin(urljoin(SITE_URL, PAGE_URL), rel_image_path)
    else:
        click.secho('Could not find map image', file=sys.stderr)

    return image_url


def _download_map_from_page(image_url, map_file_path):
    """
    Downloads the weather map image and stores it as a local file.

    :param image_url: The url of the weather map image
    :param map_file_path: The absolute path to store the image file
    :return: True if the map was downloaded and successfully stored on disk, otherwise, False
    :exception: Any exception that occurs making the HTTP request or an IOError when writing the image to disk
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


if __name__ == '__main__':
    get()
