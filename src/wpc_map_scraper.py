"""T
his program downloads historical weather maps from the Weather Prediction Center (WPC) that is part of the
National Weather Service.  Surface weather maps for North America and the Continental United States are
available from May 1, 2005 onward.  Eight different kinds of maps are available at eight different times per day.
This program will allow you to download one type of map for a range of dates, and store the maps in a folder.
"""

import requests                     # issues http requests and handles responses
import shutil                       # used to handle copying the map from a stream to a file
import sys                          # access to stderr, ...
from bs4 import BeautifulSoup       # used to parse and search the http responses
import iso8601                      # parsing standardized time strings
import datetime                     # like it says
import os.path                      # handles file creating, naming and storing
from urllib.parse import urljoin    # builds a url from pieces and parts
import time

# constants to simplify maintenance
SITE_URL = 'http://www.wpc.ncep.noaa.gov/'
PAGE_URL = 'archives/web_pages/sfc/sfc_archive_maps.php?'
MAP_DIR = './maps'
IMAGE_FILE_TYPE = 'gif'
MAP_CSS_SELECTOR = '.sfcmapimage'  # CSS class selector for the weather map
WAIT_PERIOD = 5


def build_page_url(date_and_time, map_type):
    """
    Makes the url of the page that contains the archived surface weather map.

    :param date_and_time: The datetime for the map
    :param map_type: The type of surface map to download
    :returns The url for the surface map page with the date, time and map type correctly formatted
    """
    year, month, day, hour = date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour
    return f'{SITE_URL}{PAGE_URL}arcdate={month:02d}/{day:02d}/{year}&selmap={year}{month:02d}{day:02d}{hour}&maptype={map_type}'


def make_iso_date(date_str, time_str='00'):
    """
    Makes and parses an ISO8601 compliant date string into a datetime object.

    All times are in Universal Coordinated Time (UTC) which is commonly referred to a Z or 'Zulu'.
    :param date_str: Valid date strings that have the form: YYYY-MM-DD or YYYYMMDD
    :param time_str: Valid times include: 0, 6, 12, 18. All times are UTC or 'Z'.  Defaults to OZ.
    :return: The datetime object for the specified date and time for the UTC time zone
    """
    iso_str = date_str + 'T' + time_str + 'Z'
    return iso8601.parse_date(iso_str)


def make_time_series(begin, end, times):
    """
    Makes the series of datetime objects for the period of interest.

    :param begin: Starting date for the date range (inclusive)
    :param end: Ending date (inclusive) for the date range
    :param times: List of times for daily maps
    :return: A list of datetime objects for each time and every day specified in the range
    """
    # create the starting and ending datetime objects using values provided on the command line 
    start_dt = make_iso_date(begin)
    stop_dt = make_iso_date(end)
    num_days = (stop_dt - start_dt).days  # timedelta object has a days attribute

    # reality check
    if start_dt > stop_dt:
        return []

    # build a list of datetime objects by adding incremental day and time offsets to the start date
    # note: range(value) is generates values from 0 to value - 1, therefore adding 1
    return [
        start_dt + datetime.timedelta(days=d, hours=int(t))
        for d in range(num_days+1)
        for t in times]


def get_map_path(map_dir, dt, map_type):
    """
    Makes the absolute path for the weather map image file.

    :param map_dir: Path to storage directory as a string
    :param dt: Datetime of the map
    :param map_type: The type of surface map to download
    :return: Absolute path for the weather map image file
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


def build_image_url(page_url):
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


def download_map(image_url, map_file_path):
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


def scrape_map(begin, end, map_times, map_types, map_dir=MAP_DIR):
    """
    Downloads and saves a series of weather map images to disk.

    One map of each type will be downloaded for every date and time specified.
    :param begin: Starting data and time (inclusive)
    :param end: Stopping date and time (inclusive)
    :param map_times: Valid map times can include: 0, 6, 12, 18.  All times are UTC or 'Z'
    :param map_types: Valid map types include following (note the colon is NOT part of the name):
        namussfc:     Unites States (CONUS)
        usfntsfc:     United States (Fronts/Analysis Only)
        print_us:     United States (B/W)
        ussatsfc:     U.S. Analysis/Satellite Composition
        radsfcus_exp: U.S. Analysis/Radar Composition
        namfntsfc:    North America (Fronts/Analysis Only)
        satsfcnps:    North America Analysis/Satellite Composition
    :param map_dir: Folder to store the map files in
    """
    dt_series = make_time_series(begin, end, map_times)
    for dt in dt_series:
        for map_type in map_types:
            page_url = build_page_url(dt, map_type)
            map_path = get_map_path(map_dir, dt, map_type)
            image_url = build_image_url(page_url)
            download_map(image_url, map_path)
            time.sleep(WAIT_PERIOD)


# TODO 3. Test bad / missing input values
# TODO 4. Proof read documentation
# TODO 5. Add a Readme.rst
# TODO 6. Check into github
# TODO 7. Have a beer

def main():
    pass
# TODO Handle command line arguements
# TODO Click can't handle sequences with unknown length, consider alternatives
# TODO Get Click command line working
# TODO Create a python package structure
# @click.command()
# @click.option('-b', '--begin', help='Starting date as YYYY-MM-DD or YYYYMMDD format. ')
# @click.option('-e', '--end',   help='Ending date as YYYY-MM-DD or YYYYMMDD format')
# @click.option('-t', '--times', multiple=True, help='Time(s) UTC or Z for weather map(s) (00, 06, 12, 18)')
# @click.option('-m', '--maps',  multiple=True, help='Type(s) of surface weather maps to download (namussfc, usfntsfc, print_us, ussatsfc, radsfcus_exp, namfntsfc, na_zoomin, satsfcnps)')
# def main():
#     """
#     This program downloads archived surface weather maps for a range of dates and times from the
#     Weather Prediction Center (part of the National Weather Service).
#     """
#     dt_series = build_time_series(begin, end, times)
#     scrape_map(begin, end, times, maps)


if __name__ == '__main__':
    main()
